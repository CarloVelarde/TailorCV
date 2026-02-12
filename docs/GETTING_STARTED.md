# Getting Started

## Audience

This guide is for a brand new user who just cloned TailorCV and wants the
first successful `generate` run.

## What TailorCV Depends On

- Python 3.12+
- OpenAI API access (for default LLM selection mode)
- `rendercv` Python package (used for official schema validation)
- Optional OS keychain backend (`keyring`) for storing API keys securely

If keychain is unavailable (common in WSL2/headless Linux), TailorCV still
works by using environment variables for API keys.

## Install From Fresh Clone

1. Clone and enter repository:

```bash
git clone <your-repo-url>
cd ResumeGen
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration Model (What Persists vs What Does Not)

TailorCV has two config layers:

1. Non-secret config file (provider + model defaults):

- Linux/macOS default: `~/.config/tailorcv/config.yaml`
- Windows default: `%APPDATA%\tailorcv\config.yaml`
- Optional override env var: `TAILORCV_CONFIG_PATH`

2. Secret storage (API key):

- First preference at runtime: environment variable (e.g. `OPENAI_API_KEY`)
- Fallback: OS keychain via `keyring` (if available)

Persistence summary:

- `provider`/`model` set by `init`: persistent across sessions
- API key in keychain: persistent across sessions (if keychain works)
- API key in `export OPENAI_API_KEY=...`: shell-session only unless added to shell rc file
- CLI `--api-key` flag on `generate`: one-off for that command only

## Initialize TailorCV

Recommended in WSL2/Linux (non-interactive + env var):

```bash
export OPENAI_API_KEY="YOUR_OPENAI_KEY"
python -m tailorcv init --provider openai --model gpt-4.1-mini --non-interactive
```

Interactive setup (desktop environments with keychain):

```bash
python -m tailorcv init
```

## Sample Inputs

Create `profile.yaml`:

```yaml
meta:
  name: Jane Doe
  headline: Backend Engineer
  location: Austin, TX
  email: jane.doe@example.com

education:
  - id: edu_ut
    institution: University of Texas
    area: Computer Science
    degree: B.S.

experience:
  - id: exp_api
    company: ExampleCorp
    position: Software Engineer
    highlights:
      - Built and maintained Python APIs.
      - Improved service performance and reliability.

projects:
  - id: proj_resumegen
    name: Resume Tailoring CLI
    highlights:
      - Implemented structured LLM selection with strict validation.

skills:
  - label: Languages
    details: Python, Go, SQL
  - label: Frameworks
    details: FastAPI, Flask
```

Create `job.txt`:

```text
We are hiring a backend engineer to build scalable APIs.
Experience with Python, FastAPI, SQL, and cloud deployment is preferred.
```

## First Generate Run (Default LLM Mode)

Run:

```bash
python -m tailorcv generate \
  --profile profile.yaml \
  --job job.txt \
  --out resume.yaml
```

Result:

- TailorCV generates a selection plan with the configured LLM provider/model.
- TailorCV validates selection strictly against your profile.
- TailorCV maps and validates final RenderCV YAML, then writes `resume.yaml`.

## Manual Selection Override (Debug/Repro Mode)

If you want deterministic selection input:

```bash
python -m tailorcv generate \
  --profile profile.yaml \
  --job job.txt \
  --selection selection.json \
  --out resume.yaml
```

This bypasses LLM plan generation and uses your manual selection file.

## One-Off Runtime Overrides

You can override persisted defaults for a single command:

```bash
python -m tailorcv generate \
  --profile profile.yaml \
  --job job.txt \
  --out resume.yaml \
  --provider openai \
  --model gpt-4.1-mini \
  --api-key "YOUR_OPENAI_KEY" \
  --max-attempts 3
```

## Troubleshooting

No keyring backend available:

- Use environment variables (`OPENAI_API_KEY`) and non-interactive `init`.

Invalid/missing key errors:

- Verify `OPENAI_API_KEY` is present in the current shell:
  - `echo $OPENAI_API_KEY`

Validation errors:

- TailorCV enforces strict profile/selection and RenderCV schema correctness.
- Review CLI error output and adjust profile content or override settings as needed.
