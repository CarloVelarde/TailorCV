LLM Output Contract (MVP)
=========================

Goal
----
The LLM selects and optionally rewrites profile content. It does not emit YAML.
TailorCV converts the structured output into RenderCV YAML and validates it.

Source of truth
---------------
The contract is defined in `tailorcv/llm/selection_schema.py` and should be kept in sync with this document.
Provider plumbing for generation lives in:
- `tailorcv/llm/base.py`
- `tailorcv/llm/runtime.py`
- `tailorcv/llm/router.py`
- `tailorcv/llm/providers/openai_provider.py`

Rewriting guidance
------------------
Profile bullet points are source material, not hard limits. The LLM is expected to reword, reorganize, and infer improved bullets based on the profile context and job description. Use `bullet_overrides` to provide the rewritten bullets.

Strict validation
-----------------
Selection output is strictly validated against the profile before mapping. Any
unknown IDs or labels will fail validation and must be corrected by the LLM.

Temporary requirement
---------------------
For the current MVP, users provide the selection JSON manually. This will be
replaced by automatic LLM generation in the CLI.

Output format
-------------
The LLM must return JSON with the following shape:

```
{
  "selected_experience_ids": ["exp_id_1"],
  "selected_project_ids": ["proj_id_1"],
  "selected_education_ids": ["edu_id_1"],
  "selected_skill_labels": ["Languages", "Frameworks"],
  "bullet_overrides": {
    "exp_id_1": [
      "Optional rewritten bullet 1",
      "Optional rewritten bullet 2"
    ]
  },
  "section_order": ["Experience", "Projects", "Education", "Skills"]
}
```

Notes
-----
- All fields are optional; omit keys that are not used.
- IDs must match `profile.yaml` entry IDs.
- If `bullet_overrides` is omitted for an entry, TailorCV uses the original
  highlights from the profile.
- The app will enforce output structure and fail fast on invalid JSON.

Example
-------
See `tailorcv/examples/llm_selection_example.json`.
