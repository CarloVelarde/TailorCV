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
- LLM-integration groundwork:
  - pipeline orchestration module (`tailorcv/app/pipeline.py`)
  - persisted config + keyring secret helpers (`tailorcv/config/`)
  - setup command (`tailorcv init`)
  - provider abstraction + router (`tailorcv/llm/base.py`, `tailorcv/llm/router.py`)
  - OpenAI provider implementation (`tailorcv/llm/providers/openai_provider.py`)
  - selection prompt builder (`tailorcv/llm/selection_prompt.py`)
  - selection generation service + retry loop (`tailorcv/llm/selector.py`)
  - CLI `generate` wiring with LLM-default selection and manual override

Next
----
- Add selection scoring (tags + keyword overlap).
- Expand provider coverage beyond OpenAI (Gemini/Groq/Claude).

Later
-----
- Template tuning for different resume flavors.
- Advanced keyword extraction and section weighting.
- Optional multi-step LLM prompts for rewriting.
