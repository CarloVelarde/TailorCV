LLM Output Contract (MVP)
=========================

Goal
----
The LLM selects and optionally rewrites profile content. It does not emit YAML.
TailorCV converts the structured output into RenderCV YAML and validates it.

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
