Project Status
==============

Current state (MVP)
-------------------
- Full pipeline works end-to-end using a user-provided selection JSON.
- Strict selection validation is enforced.
- Deterministic mapping and full RenderCV validation are in place.
- Defaults for design/locale/settings are applied when not overridden.
- CLI entrypoint available via `python -m tailorcv` (Typer-based).

Current limitation
------------------
- No LLM integration yet; users must manually create `selection.json` and pass `--selection`.
- No automated test suite implemented yet; see `docs/TEST_PLAN.md`.

Next step
---------
- Add LLM integration in the CLI to generate the selection plan automatically,
  including rewritten bullets, with a retry loop on validation errors.
