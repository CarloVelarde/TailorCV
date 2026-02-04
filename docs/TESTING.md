Testing Guide
=============

Goals
-----
- Fast, deterministic tests for core pipeline.
- One integration test to ensure CLI flow works end-to-end.
- Require tests after changes that affect behavior or validation.

Frameworks
----------
- `pytest`
- `typer.testing.CliRunner`

Layout
------
```
tests/
  conftest.py
  fixtures/
  test_loaders.py
  test_selection_validator.py
  test_mapper.py
  test_assembler.py
  test_cli_generate.py
```

How to run
----------
```
pytest
```

Run a subset:
```
pytest tests/test_loaders.py tests/test_selection_validator.py
```

Guidelines
----------
- Use `tmp_path` for filesystem output.
- Keep fixtures minimal and independent of `tailorcv/examples/`.
- Prefer clear failure messages and specific assertions.
- Add tests for new logic when practical; avoid brittle or overfit tests.

Phase 1 scope
-------------
See `docs/TEST_PLAN.md` for the current issue breakdown.
