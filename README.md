ResumeGen / TailorCV
====================

<p align="center">
  <a href="https://github.com/CarloVelarde/ResumeGen/actions/workflows/tests.yaml">
    <img src="https://github.com/CarloVelarde/ResumeGen/actions/workflows/tests.yaml/badge.svg" alt="CI">
  </a>
  <a href="https://codecov.io/gh/CarloVelarde/ResumeGen">
    <img src="https://codecov.io/gh/CarloVelarde/ResumeGen/branch/main/graph/badge.svg?token=M30PAVAJ1I" alt="Coverage">
  </a>
</p>

<p align="center">
  <a href="https://codecov.io/gh/CarloVelarde/ResumeGen">
    <img src="https://codecov.io/gh/CarloVelarde/ResumeGen/graphs/sunburst.svg?token=M30PAVAJ1I" alt="Codecov Sunburst">
  </a>
</p>

Vision
------
TailorCV turns a messy job description plus a global `profile.yaml` into a
RenderCV-compatible YAML file. The goal is minimal user friction:

1. User keeps a single, reusable `profile.yaml`.
2. User pastes a job description into `job.txt`.
3. TailorCV selects the most relevant profile content and outputs
   RenderCV-ready YAML.

MVP flow (hybrid LLM + deterministic build)
-------------------------------------------
1) Load `profile.yaml` into a strongly-typed Profile object.
2) Load `job.txt`, clean it, and extract keywords.
3) Send the profile + job summary to an LLM with a strict JSON output schema.
4) Strictly validate the LLM selection against the profile.
5) Use the JSON to deterministically build a RenderCV `cv` dictionary.
6) Assemble a full RenderCV document with defaults and optional overrides.
7) Validate the result using RenderCV's official Pydantic models.

The LLM does selection and optional rewriting; TailorCV does formatting,
schema compliance, and validation.

Current status
--------------
The pipeline works end-to-end using a user-provided selection JSON, but there
is no LLM integration yet. See `docs/STATUS.md` for the current state and next
step.

Inputs
------
- `profile.yaml` (user global profile)
- `job.txt` (target job description)

Profile schema (input)
----------------------
See `tailorcv/examples/sample_input_profile.yaml` for a full example.

Key points:
- `meta` is required (name, location, email). Optional fields: headline, phone,
  website, socials.
- `education`, `experience`, and `projects` allow sparse entries:
  optional `date`, `start_date`, `end_date`, `summary`, `location`,
  and `highlights`.
- `id` and `tags` are optional on entries.
- `skills`, `certifications`, and `interests` are optional lists.

Tags
----
Tags are optional keywords that help matching and selection. They can be used
as lightweight relevance signals but are never required.

RenderCV validation
-------------------
TailorCV validates generated output against RenderCV's official Pydantic models
before writing YAML. This ensures user-supplied `design`, `locale`, and
`settings` blocks are correct, and raises a clear validation error if invalid.

See `tailorcv/validators/rendercv_validator.py`.

Manual smoke test
-----------------
Run the debug script to validate the current flow (job loader, profile loader,
LLM selection plan, strict selection validation, mapper preview, document assembly, and RenderCV validation):

```bash
python -m tailorcv.debug
```

Override inputs or skip steps:

```bash
python -m tailorcv.debug --job path/to/job.txt --profile path/to/profile.yaml --rendercv path/to/cv.yaml
python -m tailorcv.debug --selection path/to/selection.json
python -m tailorcv.debug --skip-rendercv
python -m tailorcv.debug --skip-selection
python -m tailorcv.debug --skip-mapper
python -m tailorcv.debug --skip-selection-validation
python -m tailorcv.debug --skip-assembly
```

CLI usage
---------
Generate a RenderCV YAML file (file path or directory):

```bash
python -m tailorcv generate \
  --profile path/to/profile.yaml \
  --job path/to/job.txt \
  --selection path/to/selection.json \
  --out path/to/output.yaml

# Or write to a directory (writes rendercv_output.yaml inside it)
python -m tailorcv generate \
  --profile path/to/profile.yaml \
  --job path/to/job.txt \
  --selection path/to/selection.json \
  --out path/to/output_dir
```

Note: `--selection` is required for the current MVP. This will become optional
once LLM selection generation is integrated.

Optional overrides:

```bash
python -m tailorcv generate \
  --profile path/to/profile.yaml \
  --job path/to/job.txt \
  --selection path/to/selection.json \
  --out path/to/output.yaml \
  --design path/to/design.yaml \
  --locale path/to/locale.yaml \
  --settings path/to/settings.yaml
```

Debug:

```bash
python -m tailorcv debug
```

Testing
-------
Run all tests:

```bash
pytest
```

Run a subset:

```bash
pytest tests/test_loaders.py tests/test_selection_validator.py
```

Coverage:

```bash
pytest --cov=tailorcv --cov-report=term-missing
```

Makefile shortcuts
------------------
```
make lint
make format
make format-check
make test
make coverage
make debug
make generate
```

Repository layout
-----------------
- `tailorcv/defaults/`: One-page-biased defaults for design/locale/settings.
- `tailorcv/assemblers/`: Assemble full RenderCV documents with overrides.
- `tailorcv/loaders/`: Load and validate profile and job inputs.
- `tailorcv/mappers/`: Deterministic mapping from profile + LLM plan to RenderCV.
- `tailorcv/schema/`: Pydantic models for profile input and RenderCV targets.
- `tailorcv/validators/`: RenderCV official schema validation helpers.
- `tailorcv/examples/`: Sample input files.
- `tailorcv/debug.py`: Manual smoke test entrypoint.

Docs
----
- `docs/VISION.md`: Product vision and principles.
- `docs/ARCHITECTURE.md`: Data flow and module roles.
- `docs/LLM_CONTRACT.md`: LLM JSON output contract.
- `docs/ROADMAP.md`: MVP and next steps.
- `docs/STYLEGUIDE.md`: Formatting, naming, and docstring conventions.
- `docs/DECISIONS.md`: Rationale for key MVP decisions.
- `docs/STATUS.md`: Current product status and next step.
- `docs/TEST_PLAN.md`: Temporary Phase 1 test plan.
- `docs/TESTING.md`: How to run tests and layout.

Acknowledgements
----
This project is built on top of RenderCV, which is licensed under the MIT License.
