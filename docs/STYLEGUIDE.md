Style Guide
===========

Scope
-----
Keep this project consistent, readable, and easy to lint and format.

Conventions
-----------
- Python formatting and linting: Ruff (see `pyproject.toml`).
- Naming: snake_case for variables/functions, PascalCase for classes.
- Docstrings: Sphinx format, e.g. ``:param``, ``:type``, ``:return``, ``:rtype``.
- Types: use type hints for public functions.
- Comments: short and rare; explain "why" over "what".

Linting
-------
- Run Ruff before pushing changes.
- CI should enforce Ruff formatting and linting.
