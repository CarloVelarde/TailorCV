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

Current limitation
------------------
- No LLM integration yet; users must manually create `selection.json` and pass `--selection`.
- Persisted LLM config is currently setup-only and is not consumed by
  `generate` until LLM selection is integrated.

Testing status
--------------
- Phase 1 tests TEST-001 through TEST-008 implemented.
- Added tests for pipeline orchestration, config storage, secret resolution,
  and `tailorcv init` non-interactive setup paths.

Next step
---------
- Integrate OpenAI selection generation in the CLI and make it the default
  selection source.
- Add retry loop on strict selection validation failures.
- Keep manual `--selection` path for debugging/reproducibility.
