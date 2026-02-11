Test Plan (Completed)
=====================

Purpose
-------
Define Phase 1 tests before LLM integration. These are isolated, deterministic,
and focused on meaningful failures.

Issue List (Phase 1)
--------------------
TEST-001: Profile loader happy + bad path (implemented)
-----------------------------------------
- Scope: `tailorcv/loaders/profile_loader.py`
- Fixtures: `fixtures/profile_valid.yaml`, `fixtures/profile_invalid.yaml`
- Steps:
  1) Load valid profile -> assert Profile object.
  2) Load invalid profile -> assert `ProfileLoadError`.
- Assertions:
  - Valid profile: `meta.name` is set.
  - Invalid profile: exception message mentions schema validation.

TEST-002: Job loader keyword extraction baseline (implemented)
------------------------------------------------
- Scope: `tailorcv/loaders/job_loader.py`
- Fixtures: `fixtures/job_min.txt`
- Steps:
  1) Load job -> assert `Job.cleaned_text` is non-empty.
  2) Assert at least one lexicon term appears in keywords.
- Edge case: noisy text with emails/URLs should not raise.

TEST-003: Selection validator unknown IDs (implemented)
-----------------------------------------
- Scope: `tailorcv/validators/selection_validator.py`
- Fixtures: `fixtures/selection_invalid_id.json`, `fixtures/profile_valid.yaml`
- Steps:
  1) Validate plan -> expect `SelectionValidationFailure`.
- Assertions:
  - Error list includes unknown ID message.

TEST-004: Selection validator empty resume (implemented)
------------------------------------------
- Scope: `tailorcv/validators/selection_validator.py`
- Fixtures: `fixtures/selection_empty.json`, `fixtures/profile_empty.yaml`
- Steps:
  1) Validate plan -> expect `SelectionValidationFailure`.
- Assertions:
  - Error list includes empty resume message.

TEST-005: Mapper output structure (implemented)
---------------------------------
- Scope: `tailorcv/mappers/rendercv_mapper.py`
- Fixtures: `fixtures/profile_valid.yaml`, `fixtures/selection_valid.json`
- Steps:
  1) Build cv dict -> assert sections exist.
  2) Ensure empty fields are omitted (no empty highlights).
- Assertions:
  - `cv.sections` contains expected keys.

TEST-006: Mapper respects bullet overrides (implemented)
------------------------------------------
- Scope: `tailorcv/mappers/rendercv_mapper.py`
- Fixtures: `fixtures/selection_overrides.json`, `fixtures/profile_valid.yaml`
- Steps:
  1) Build cv dict -> assert highlights match overrides.

TEST-007: Assembler defaults + overrides (implemented)
----------------------------------------
- Scope: `tailorcv/assemblers/rendercv_document.py`
- Fixtures: optional design/locale/settings overrides
- Steps:
  1) Assemble with no overrides -> defaults present.
  2) Assemble with overrides -> overrides take precedence.
- Assertions:
  - Output contains `cv`, `design`, `locale`, `settings`.

TEST-008: CLI generate integration (implemented)
----------------------------------
- Scope: `tailorcv/cli/generate.py`
- Fixtures: `fixtures/profile_valid.yaml`, `fixtures/job_min.txt`,
  `fixtures/selection_valid.json`
- Steps:
  1) Run `tailorcv generate` via Typer `CliRunner`.
  2) Assert output YAML exists.
  3) Validate output with `validate_rendercv_document`.
- Assertions:
  - Exit code is 0.
  - Output file is created and valid.

Notes
-----
- Keep fixtures minimal; avoid coupling to `tailorcv/examples/`.
- Prefer contains/assertion checks over exact ordering.
- Add new test items here when adding behavior that should be validated.
- LLM-integration foundation tests have also been added for:
  - pipeline orchestration module behavior
  - persisted config read/write paths
  - API key env/keyring resolution
  - `tailorcv init` command non-interactive setup paths
