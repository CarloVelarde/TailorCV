Architecture Overview
=====================

Data flow
---------
1) Load profile.yaml -> Profile model
2) Load job.txt -> Job model (cleaned text + keywords)
3) LLM selection -> JSON selection plan
4) Deterministic mapper -> RenderCV YAML dictionary
5) RenderCV validation -> RenderCVModel

Optional inputs
---------------
- Users may provide `design`, `locale`, or `settings` blocks.
- If provided, these are validated with RenderCV models and must be correct.
- If omitted, TailorCV applies defaults (one-page bias).

Key modules
-----------
- `tailorcv/loaders/`: Input loading and validation.
- `tailorcv/schema/`: Pydantic schemas for profile and RenderCV targets.
- `tailorcv/validators/`: Official RenderCV validation.
- `tailorcv/cli/`: CLI entrypoints (planned).

Design goals
------------
- Keep parsing lightweight and transparent.
- Keep schemas aligned with RenderCV expectations.
- Fail fast with clear validation errors.
