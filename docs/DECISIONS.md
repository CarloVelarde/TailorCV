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
