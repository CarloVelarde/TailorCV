Project Status
==============

Current state (MVP)
-------------------
- Full pipeline works end-to-end with LLM selection as the default path.
- Strict selection validation is enforced.
- Deterministic mapping and full RenderCV validation are in place.
- Defaults for design/locale/settings are applied when not overridden.
- CLI entrypoint available via `python -m tailorcv` (Typer-based).
- Generation orchestration has been extracted to `tailorcv/app/pipeline.py`.
- First-run setup command available via `python -m tailorcv init`.
- Persisted config for LLM defaults (`provider`, `model`) is available.
- API key resolution is implemented as: environment variable -> OS keychain.
- Provider abstraction layer is implemented in `tailorcv/llm/` with
  an OpenAI provider implementation (`tailorcv/llm/providers/openai_provider.py`).
- Selection-generation service is implemented in:
  - `tailorcv/llm/selection_prompt.py` (prompt builder)
  - `tailorcv/llm/selector.py` (runtime resolve + provider call + retry loop)
- CLI `generate` now uses selector service by default and supports
  `--selection` as a manual override for debug/repro workflows.

Current limitation
------------------
- LLM integration currently targets OpenAI provider only.
- Live provider behavior is not exercised in CI (tests mock provider clients).

Testing status
--------------
- Phase 1 tests TEST-001 through TEST-008 implemented.
- Added tests for pipeline orchestration, config storage, secret resolution,
  and `tailorcv init` non-interactive setup paths.
- Added tests for LLM runtime config resolution, provider routing, and OpenAI
  structured-response parsing behavior.
- Added tests for selection prompt construction and selector retry behavior.
- Added tests for `generate` default LLM path and manual `--selection` override.

Next step
---------
- Add selection scoring (tags + keyword overlap) to improve ranking quality.
- Expand provider support beyond OpenAI using existing router abstraction.
