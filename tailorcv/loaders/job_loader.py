from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from schema.job_schema import Job


class JobLoadError(Exception):
    pass


# -------------------------
# Tuning knobs (MVP)
# -------------------------

STOPWORDS = {
    "the",
    "and",
    "or",
    "to",
    "of",
    "in",
    "for",
    "with",
    "on",
    "at",
    "is",
    "are",
    "as",
    "an",
    "a",
    "by",
    "this",
    "that",
    "will",
    "be",
    "you",
    "your",
    "we",
    "our",
    "us",
    "from",
    "they",
    "their",
    "it",
    "about",
    "role",
    "team",
    "work",
    "working",
    "ability",
    "skills",
    "experience",
    "required",
    "preferred",
    "responsibilities",
    "qualifications",
    "including",
    "within",
    "across",
}

# Lines containing these (case-insensitive) are often page chrome/legal/footer.
# We apply them conservatively (line level skips), so important content still survives elsewhere.
NOISE_LINE_PATTERNS = [
    r"\bcookie\b",
    r"\bprivacy\b",
    r"\bterms\b",
    r"\bequal opportunity\b",
    r"\ball qualified applicants\b",
    r"\baccessibility\b",
    r"\ball rights reserved\b",
    r"\bsubscribe\b",
    r"\bsign up\b",
    r"\bget notified\b",
    r"\baccept all\b",
    r"\bmore options\b",
    r"\bshare job\b",
    r"\bsave job\b",
    r"\bapply now\b",
    r"\bback to\b",
    r"\bview all\b",
    r"\bfraudulent\b",
    r"\bsite map\b",
]

# Pattern helpers
_EMAIL_RE = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", re.IGNORECASE)
_URL_RE = re.compile(r"\bhttps?://\S+|\bwww\.\S+", re.IGNORECASE)

# Token regex designed for tech:
# - supports c++, c#, node.js, .net, ci/cd, react-native, gRPC, etc.
_TOKEN_RE = re.compile(
    r"""
    (?:
        [a-zA-Z]                                  # starts with letter
        [a-zA-Z0-9\+\#\.\-/]*                      # allow tech punctuation
    )
""",
    re.VERBOSE,
)

# Tokens that are *very likely* junk if they match these patterns
JUNK_TOKEN_PATTERNS = [
    re.compile(r"^\d+$"),  # all numbers
    re.compile(r"^[a-z]{1,2}\d{3,}$", re.I),  # ids like: jr202518329
    re.compile(r"^\w{12,}$"),  # long random words often ids (handled carefully below)
]


def load_job(
    job_path: str | Path,
    *,
    lexicon_path: str | Path | None = None,
    max_keywords: int = 50,
) -> Job:
    """
    Load a job posting from a .txt file, clean it, and extract keywords.

    - lexicon_path (optional): path to a newline-delimited list of tech terms/phrases.
      If None, uses "resources/tech_lexicon.txt" relative to project root (best effort).
    """
    job_path = Path(job_path)
    if not job_path.exists():
        raise JobLoadError(f"Job file not found: {job_path}")

    try:
        raw_text = job_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        raise JobLoadError(f"Failed to read job file: {e}")

    cleaned_text = _clean_text(raw_text)

    lexicon_terms = _load_lexicon(lexicon_path)
    keywords = _extract_keywords(
        cleaned_text=cleaned_text,
        lexicon_terms=lexicon_terms,
        max_keywords=max_keywords,
    )

    return Job(
        raw_text=raw_text,
        cleaned_text=cleaned_text,
        keywords=keywords,
    )


# -------------------------
# Cleaning
# -------------------------


def _clean_text(text: str) -> str:
    """
    Conservative cleaner:
    - removes obvious UI/footer/legal lines
    - removes emails/urls (they create junk tokens)
    - normalizes whitespace
    - keeps the bulk of content (we do NOT attempt “section parsing”)
    """
    # Remove invisible/control-ish whitespace that can break tokenization
    text = text.replace("\u200b", " ").replace("\ufeff", " ")

    lines = text.splitlines()
    kept: list[str] = []

    for line in lines:
        s = line.strip()
        if not s:
            continue

        lower = s.lower()

        # Skip short pure-navigation lines like "next", "previous", "apply"
        if len(lower) <= 3:
            continue

        # Remove lines that look like pure UI chrome (but do NOT overdo it)
        if any(re.search(p, lower) for p in NOISE_LINE_PATTERNS):
            continue

        # Remove emails/urls inside the line (don’t drop whole line)
        s = _EMAIL_RE.sub(" ", s)
        s = _URL_RE.sub(" ", s)

        kept.append(s)

    cleaned = " ".join(kept)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


# -------------------------
# Lexicon loading
# -------------------------


def _load_lexicon(lexicon_path: str | Path | None) -> list[str]:
    """
    Loads lexicon terms from a newline delimited .txt file

    Format:
      - one term per line
      - supports phrases (e.g., "machine learning")
      - supports comments with "#"
    """
    candidate_paths: list[Path] = []

    if lexicon_path is not None:
        candidate_paths.append(Path(lexicon_path))
    else:
        # Best effort default: resources/tech_lexicon.txt relative to working dir
        candidate_paths.append(Path("resources") / "tech_lexicon.txt")
        # Also try relative to this file: io/../resources/tech_lexicon.txt
        candidate_paths.append(
            Path(__file__).resolve().parent.parent / "resources" / "tech_lexicon.txt"
        )

    for p in candidate_paths:
        if p.exists():
            terms: list[str] = []
            for raw_line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                # Allow inline comments: "kubernetes  # orchestration"
                if "#" in line:
                    line = line.split("#", 1)[0].strip()
                if line:
                    terms.append(_norm_term(line))
            # Unique, stable order
            seen = set()
            out = []
            for t in terms:
                if t not in seen:
                    seen.add(t)
                    out.append(t)
            return out

    # No lexicon file found — still works via frequency-only fallback.
    return []


def _norm_term(term: str) -> str:
    return re.sub(r"\s+", " ", term.strip().lower())


# -------------------------
# Keyword extraction
# -------------------------


def _extract_keywords(
    *,
    cleaned_text: str,
    lexicon_terms: list[str],
    max_keywords: int,
) -> list[str]:
    """
    Combine:
      1) lexicon matches (high-signal, even if mentioned once)
      2) frequency-derived tokens (discovery for unknown tech)

    Returns unique keywords in priority order.
    """
    text_lower = cleaned_text.lower()

    # 1) Lexicon matches (phrases + single terms)
    lexicon_hits = _find_lexicon_hits(text_lower, lexicon_terms)

    # 2) Frequency tokens (filtered)
    freq_tokens = _frequency_keywords(text_lower)

    # Merge:
    # - keep lexicon hits first (high precision)
    # - then fill with top frequency tokens not already included
    out: list[str] = []
    seen = set()

    for k in lexicon_hits:
        if k not in seen:
            seen.add(k)
            out.append(k)
        if len(out) >= max_keywords:
            return out[:max_keywords]

    for k in freq_tokens:
        if k not in seen:
            seen.add(k)
            out.append(k)
        if len(out) >= max_keywords:
            break

    return out[:max_keywords]


def _find_lexicon_hits(text_lower: str, lexicon_terms: list[str]) -> list[str]:
    """
    Finds lexicon terms in the text (best-effort, safe).
    We do:
      - exact substring checks for phrases (fast)
      - boundary-ish regex for short single tokens where substring would be too loose

    Note: We don't try to extract variants (AI can normalize later).
    """
    if not lexicon_terms:
        return []

    hits: list[tuple[int, str]] = []

    for term in lexicon_terms:
        if not term:
            continue

        # Phrases: simple substring match is surprisingly robust.
        if " " in term:
            idx = text_lower.find(term)
            if idx != -1:
                hits.append((idx, term))
            continue

        # Single tokens: use a boundary-ish regex that still allows C++, C#, node.js, etc.
        # We avoid \b because '.' '+' '#' break word boundaries.
        pattern = re.compile(
            rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", re.IGNORECASE
        )
        m = pattern.search(text_lower)
        if m:
            hits.append((m.start(), term))

    # Sort by first appearance (more “job-relevant” ordering) then stable
    hits.sort(key=lambda x: x[0])
    return [t for _, t in hits]


def _frequency_keywords(text_lower: str, max_candidates: int = 80) -> list[str]:
    """
    Frequency-based discovery for terms not in lexicon.
    Aggressive junk filtering, but tries not to drop real tech.
    """
    raw_tokens = _TOKEN_RE.findall(text_lower)

    tokens: list[str] = []
    for t in raw_tokens:
        tt = t.strip("._-/").lower()
        if not tt:
            continue

        # Hard junk filters
        if "@" in tt:
            continue
        if tt.startswith("http") or tt.startswith("www"):
            continue
        if tt in STOPWORDS:
            continue
        if len(tt) <= 2:
            continue

        # Filter tokens that are mostly punctuation or extremely long
        if len(tt) > 32:
            continue

        # Drop obvious IDs / numbers
        if any(p.match(tt) for p in JUNK_TOKEN_PATTERNS):
            # BUT: don't accidentally drop "k8s", "c++", "c#"
            if tt in {"k8s", "c++", "c#"}:
                tokens.append(tt)
            continue

        # Drop tokens that look like file hashes / random strings:
        # heuristic: long and no vowels (often IDs)
        if len(tt) >= 12 and not re.search(r"[aeiou]", tt):
            continue

        tokens.append(tt)

    counts = Counter(tokens)
    common = [w for w, _ in counts.most_common(max_candidates)]

    # Light post filter: avoid generic “soft” words that slip through
    common = [w for w in common if w not in {"team", "work", "role", "great", "able"}]

    return common
