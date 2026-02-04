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
- CLI expects a selection JSON file for MVP.
- LLM integration and retry loop will live in the CLI layer.
