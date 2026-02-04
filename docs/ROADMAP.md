Roadmap
=======

Now (MVP)
---------
- Load and validate profile.yaml.
- Parse job.txt and extract keywords.
- Collect LLM selection output (JSON) with optional rewritten bullets.
- Strictly validate selection against the profile.
- Build RenderCV `cv` dict deterministically.
- Assemble full document with defaults and optional overrides.
- CLI `tailorcv generate` command to run the pipeline.
- Validate with RenderCV official models.

Next
----
- Integrate LLM selection generation in the CLI (no manual JSON).
- Add selection scoring (tags + keyword overlap).
- Add retry strategy on validation errors.

Later
-----
- Template tuning for different resume flavors.
- Advanced keyword extraction and section weighting.
- Optional multi-step LLM prompts for rewriting.
