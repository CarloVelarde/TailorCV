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
- `pytest-cov` for coverage reporting
- `typer.testing.CliRunner`

Layout
------
```
tests/
  conftest.py
  fixtures/
  test_config_store.py
  test_secrets.py
  test_loaders.py
  test_selection_validator.py
  test_mapper.py
  test_assembler.py
  test_pipeline.py
  test_cli_init.py
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

Coverage
--------
```
pytest --cov=tailorcv --cov-report=term-missing
```

CI
--
GitHub Actions runs linting and tests and uploads coverage to Codecov.

Makefile shortcuts
------------------
```
make test
make coverage
make lint
make format
make format-check
```

Pytest config
-------------
Pytest uses `pyproject.toml` for configuration:

```
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"
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
