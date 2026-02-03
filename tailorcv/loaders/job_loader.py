"""Job description loader and keyword extractor."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from tailorcv.schema.job_schema import Job


class JobLoadError(Exception):
    """Raised when a job description cannot be loaded or parsed."""

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
    Load a job posting from a text file, clean it, and extract keywords.

    :param job_path: Path to the job description text file.
    :type job_path: str | pathlib.Path
    :param lexicon_path: Optional path to a newline-delimited lexicon file.
        If omitted, the loader will try a default in ``resources/tech_lexicon.txt``.
    :type lexicon_path: str | pathlib.Path | None
    :param max_keywords: Maximum number of keywords to return.
    :type max_keywords: int
    :return: Parsed job content with cleaned text and extracted keywords.
    :rtype: tailorcv.schema.job_schema.Job
    :raises JobLoadError: If the file does not exist or cannot be read.
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
    Clean and normalize job text without heavy structure assumptions.

    The cleaner removes obvious UI/footer/legal lines, strips emails and URLs,
    and normalizes whitespace while preserving the core content.

    :param text: Raw job description text.
    :type text: str
    :return: Cleaned, single-line text suitable for tokenization.
    :rtype: str
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
    Load lexicon terms from a newline-delimited text file.

    Format rules:
    - one term per line
    - phrases allowed (e.g., "machine learning")
    - comments allowed with "#"

    :param lexicon_path: Optional path to a lexicon file.
    :type lexicon_path: str | pathlib.Path | None
    :return: Normalized lexicon terms.
    :rtype: list[str]
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
    """
    Normalize a lexicon term for comparison.

    :param term: Raw lexicon term.
    :type term: str
    :return: Normalized term.
    :rtype: str
    """
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
    Extract prioritized keywords from cleaned text.

    The strategy combines:
    1) lexicon matches (high-signal, even when mentioned once)
    2) frequency-derived tokens (discovery for unknown terms)

    :param cleaned_text: Cleaned job description text.
    :type cleaned_text: str
    :param lexicon_terms: Normalized lexicon terms.
    :type lexicon_terms: list[str]
    :param max_keywords: Maximum number of keywords to return.
    :type max_keywords: int
    :return: Unique keywords in priority order.
    :rtype: list[str]
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
    Find lexicon terms in the text (best-effort, safe).

    This uses substring checks for phrases and boundary-aware matching for
    single tokens. It does not attempt variant expansion.

    :param text_lower: Lowercased cleaned job text.
    :type text_lower: str
    :param lexicon_terms: Normalized lexicon terms.
    :type lexicon_terms: list[str]
    :return: Lexicon hits in order of first appearance.
    :rtype: list[str]
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
        pattern = re.compile(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", re.IGNORECASE)
        m = pattern.search(text_lower)
        if m:
            hits.append((m.start(), term))

    # Sort by first appearance (more “job-relevant” ordering) then stable
    hits.sort(key=lambda x: x[0])
    return [t for _, t in hits]


def _frequency_keywords(text_lower: str, max_candidates: int = 80) -> list[str]:
    """
    Extract frequent tokens not captured by the lexicon.

    Aggressive junk filtering is applied while attempting to preserve
    genuine technical terms.

    :param text_lower: Lowercased cleaned job text.
    :type text_lower: str
    :param max_candidates: Maximum number of candidate tokens to consider.
    :type max_candidates: int
    :return: Candidate keywords by frequency.
    :rtype: list[str]
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
