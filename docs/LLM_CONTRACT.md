LLM Output Contract (MVP)
=========================

Goal
----
The LLM selects and optionally rewrites profile content. It does not emit YAML.
TailorCV converts the structured output into RenderCV YAML and validates it.

Source of truth
---------------
The contract is defined in `tailorcv/llm/selection_schema.py` and should be kept in sync with this document.

Rewriting guidance
------------------
Profile bullet points are source material, not hard limits. The LLM is expected to reword, reorganize, and infer improved bullets based on the profile context and job description. Use `bullet_overrides` to provide the rewritten bullets.

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
