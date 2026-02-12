Architecture Overview
=====================

Data flow (current)
-------------------
1) Load profile.yaml -> Profile model
2) Load job.txt -> Job model (cleaned text + keywords)
3) Load selection plan from user-provided JSON
4) Strict selection validation -> profile + plan consistency
5) Deterministic mapper -> RenderCV `cv` dictionary
6) Assemble full document with defaults/overrides
7) RenderCV validation -> RenderCVModel

Data flow (next: LLM-integrated)
--------------------------------
1) Resolve persisted/default runtime config -> provider/model defaults
2) Load profile.yaml -> Profile model
3) Load job.txt -> Job model (cleaned text + keywords)
4) Build selection prompt payload from profile + job context
5) Generate selection plan via provider (OpenAI first)
6) Retry with validation/provider feedback when plan is invalid
7) Strict selection validation -> profile + plan consistency
8) Deterministic mapper -> RenderCV `cv` dictionary
9) Assemble full document with defaults/overrides
10) RenderCV validation -> RenderCVModel

Optional inputs
---------------
- Users may provide `design`, `locale`, or `settings` blocks.
- If provided, these are validated with RenderCV models and must be correct.
- If omitted, TailorCV applies defaults (one-page bias).
- Users can persist LLM defaults (`provider`, `model`) via `tailorcv init`.
- API keys are read from environment variables first, then OS keychain.

Key modules
-----------
- `tailorcv/app/`: Pipeline orchestration for end-to-end generation.
- `tailorcv/llm/`: LLM contracts, runtime config resolution, provider router.
- `tailorcv/llm/providers/`: Concrete provider implementations (OpenAI first).
- `tailorcv/llm/selection_prompt.py`: Provider-agnostic prompt payload builder.
- `tailorcv/llm/selector.py`: Selection generation service + retry loop.
- `tailorcv/defaults/`: One-page-biased defaults for design/locale/settings.
- `tailorcv/assemblers/`: Assemble full RenderCV documents with overrides.
- `tailorcv/config/`: Persistent config + secret helpers (keyring/env).
- `tailorcv/loaders/`: Input loading and validation.
- `tailorcv/mappers/`: Deterministic mapping to RenderCV structures.
- `tailorcv/schema/`: Pydantic schemas for profile and RenderCV targets.
- `tailorcv/validators/`: Official RenderCV validation.
- `tailorcv/cli/`: CLI entrypoints.

Design goals
------------
- Keep parsing lightweight and transparent.
- Keep schemas aligned with RenderCV expectations.
- Fail fast with clear validation errors.

Design decisions
----------------
See `docs/DECISIONS.md` for recorded rationale on defaults and MVP choices.
