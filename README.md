ResumeGen / TailorCV
====================

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
6) Validate the result using RenderCV's official Pydantic models.

The LLM does selection and optional rewriting; TailorCV does formatting,
schema compliance, and validation.

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
LLM selection plan, strict selection validation, mapper preview, and RenderCV validation):

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
```

Repository layout
-----------------
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
