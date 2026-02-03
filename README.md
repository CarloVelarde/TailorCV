ResumeGen / TailorCV
====================

This project builds a pipeline that takes a messy job description plus a global
`profile.yaml`, selects the most relevant profile content, and outputs a
RenderCV-compatible YAML file.

Current focus
-------------
- Define schemas that closely mirror RenderCV.
- Normalize and validate profile input.
- Extract job keywords for downstream matching.

Profile schema (input)
----------------------
See `tailorcv/examples/sample_input_profile.yaml` for a full example.

Key points:
- `meta` is required (name, location, email). Optional fields: headline, phone,
  website, socials.
- `education`, `experience`, and `projects` entries allow sparse data:
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
`settings` blocks are correct, and raises a clear validation error if they are
invalid.

See `tailorcv/validators/rendercv_validator.py` for the validation helper.
