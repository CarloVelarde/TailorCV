AGENTS
======

Purpose
-------
This file summarizes expectations for contributors and agents working on this repo.

CI
--
- Run `ruff check .` and `ruff format --check .` to lint and format code.
- Run tests after code changes that affect behavior or validation.
- Run `pytest` for test verification.
- Add tests for new logic when meaningful (favor small, deterministic tests).
- CI should fail if Ruff formatting, linting, or tests fail.

Project context
---------------
- Keep `docs/VISION.md` and `docs/ROADMAP.md` in mind during development.
- Keep the `docs/` directory up to date when behavior changes or decisions are made.
- If plans change, update relevant docs and confirm with the project owner.
