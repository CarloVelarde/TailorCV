TailorCV Vision
===============

Mission
-------
Make resume tailoring fast and low-friction by combining a stable global
profile with a job description, producing a RenderCV-compatible YAML file.

Core principles
---------------
- Deterministic structure: the app builds RenderCV YAML itself.
- LLM as selector: the LLM chooses and optionally rewrites content, but never
  formats the final YAML.
- Strict validation: all output must pass RenderCV's official schema models.
- Low friction: a single profile.yaml reused for every job.
- One-page bias: defaults target a one-page resume; users can tweak YAML as needed.

MVP scope
---------
- Inputs: `profile.yaml` and `job.txt`.
- LLM output: strict JSON schema for selection and optional rewrites.
- Output: RenderCV YAML, validated by official RenderCV models.
