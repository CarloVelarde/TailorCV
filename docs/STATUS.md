Project Status
==============

Current state (MVP)
-------------------
- Full pipeline works end-to-end using a user-provided selection JSON.
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

Current limitation
------------------
- No LLM integration yet; users must manually create `selection.json` and pass `--selection`.
- Persisted LLM config is currently setup-only and is not consumed by
  `generate` until LLM selection is integrated.
- OpenAI provider is not yet wired into `generate`; selection still comes from
  user-provided `--selection`.
- Selection generation service is not yet wired into `generate`; the command
  still requires manual `--selection` until CLI integration is completed.

Testing status
--------------
- Phase 1 tests TEST-001 through TEST-008 implemented.
- Added tests for pipeline orchestration, config storage, secret resolution,
  and `tailorcv init` non-interactive setup paths.
- Added tests for LLM runtime config resolution, provider routing, and OpenAI
  structured-response parsing behavior.
- Added tests for selection prompt construction and selector retry behavior.

Next step
---------
- Wire selector service into `generate` so LLM selection is the default path.
- Keep manual `--selection` path for debugging/reproducibility.
