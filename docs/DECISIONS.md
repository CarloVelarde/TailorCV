Decisions Log
=============

Purpose
-------
Quick reference for key MVP decisions and the rationale behind them.

Defaults: RenderCV design/locale/settings
-----------------------------------------
Why:
- Keep MVP output stable and schema-safe.
- Bias toward one-page output without over-constraining user customization.

Design
------
- Default theme: `engineeringresumes`.
- Conservative margins and font sizes to reduce overflow risk.
- Intentionally minimal block to reduce schema errors.

Locale
------
- Default to `{"language": "english"}` (RenderCV discriminator).
- RenderCV defaults to English; we avoid assumptions about formats/labels.
- Future expansion: date formats, localized section labels, numeric formats.

Settings
--------
- Default to `{}` and rely on RenderCV defaults.
- Avoid coupling to `current_date` or output paths until CLI is finalized.

LLM output contract
-------------------
- LLM returns structured JSON, not YAML.
- JSON is validated before mapping; mapping stays deterministic.
- Rewritten bullets are allowed via `bullet_overrides`.

Selection validation
--------------------
- Strict validation against profile IDs/labels.
- Fail fast on unknown IDs or empty resulting resume.
- Retry loop belongs to the LLM/CLI layer, not the mapper.

Mapping and assembly
--------------------
- Mapper is pure: `Profile + Plan -> RenderCV cv dict`.
- Assembler injects defaults and optional overrides for design/locale/settings.

CLI generation
--------------
- CLI expects a selection JSON file for MVP (temporary).
- LLM integration and retry loop will live in the CLI layer.
- CLI is Typer-based for modern UX and consistency with RenderCV.

Pipeline orchestration module
-----------------------------
- Added `tailorcv/app/pipeline.py` to own the generation call graph.
- Rationale:
  - Keeps CLI commands thin and focused on IO/UX concerns.
  - Creates a reusable orchestration seam for both manual and LLM selection modes.
  - Reduces risk of logic drift between CLI commands and future integrations.

LLM config persistence and secret handling
------------------------------------------
- Persist non-secret LLM defaults (`provider`, `model`) in config file:
  - Linux/macOS default: `~/.config/tailorcv/config.yaml`
  - Windows default: `%APPDATA%\\tailorcv\\config.yaml`
  - Optional override: `TAILORCV_CONFIG_PATH`
- Store API keys in OS keychain via `keyring`.
- API key resolution order:
  1) environment variable (provider-specific, e.g. `OPENAI_API_KEY`)
  2) OS keychain entry
- Rationale:
  - Avoid plaintext API keys in config files.
  - Keep CI/headless usage straightforward via env vars.
  - Preserve one-time local setup UX for end users.

Setup command strategy
----------------------
- Added `tailorcv init` as explicit setup command.
- Interactive mode prompts on first run; non-interactive mode supports CI/scripts.
- Rationale:
  - Explicit setup is predictable and scriptable.
  - Avoids surprising prompts in non-interactive contexts.

Init persistence ordering
-------------------------
- `tailorcv init` stores/validates API key handling before writing config.
- Rationale:
  - Avoids partially-applied setup state where config is saved but secret handling fails.
  - Keeps setup outcomes more atomic and easier to reason about.

Provider abstraction strategy
-----------------------------
- Added a provider protocol (`tailorcv/llm/base.py`) and provider router
  (`tailorcv/llm/router.py`) before wiring generation flow to OpenAI.
- Rationale:
  - Keeps OpenAI-specific code isolated from orchestration and schema logic.
  - Supports incremental provider additions (Gemini, Groq, Claude) without
    changing mapper/validator internals.
  - Keeps issue boundaries clean: provider plumbing first, selection workflow next.

OpenAI provider loading behavior
--------------------------------
- OpenAI SDK client creation is lazy in `OpenAiProvider`.
- Rationale:
  - Importing TailorCV modules should not fail in environments where `openai`
    is not installed yet.
  - Enables deterministic provider tests with injected fake clients.

Selection generation service seam
---------------------------------
- Added a dedicated selector service (`tailorcv/llm/selector.py`) instead of
  embedding LLM calls directly into CLI commands.
- Rationale:
  - Preserves clean separation between UX/IO (`cli/`) and generation behavior (`llm/`).
  - Creates a reusable entrypoint for both CLI and potential API integrations.
  - Keeps retry/error handling testable without invoking CLI.

Prompt-builder + retry feedback loop
------------------------------------
- Added provider-agnostic prompt construction in `tailorcv/llm/selection_prompt.py`.
- Selector retries are bounded (`max_attempts`) and feed prior validation/provider
  errors into subsequent attempts.
- Rationale:
  - Keeps prompt content explicit and inspectable.
  - Uses strict validator output as direct correction signals for the next attempt.
  - Avoids infinite loops and provides deterministic failure reporting.
