Roadmap
=======

Now (MVP)
---------
- Load and validate profile.yaml.
- Parse job.txt and extract keywords.
- Collect LLM selection output (JSON) with optional rewritten bullets.
- Strictly validate selection against the profile.
- Build RenderCV `cv` dict deterministically.
- Validate with RenderCV official models.

Next
----
- Add CLI `tailorcv generate`.
- Add default design/locale/settings targeting one page.
- Add selection scoring (tags + keyword overlap).
- Add retry strategy on validation errors.

Later
-----
- Template tuning for different resume flavors.
- Advanced keyword extraction and section weighting.
- Optional multi-step LLM prompts for rewriting.
