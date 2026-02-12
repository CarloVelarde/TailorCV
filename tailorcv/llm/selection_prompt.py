"""Prompt construction for LLM-driven selection plan generation."""

from __future__ import annotations

import json
from typing import Any, Sequence

from tailorcv.llm.base import LlmInvocation
from tailorcv.schema.job_schema import Job
from tailorcv.schema.profile_schema import Profile

_SYSTEM_PROMPT = """
You are an assistant that selects resume content from a provided profile for a specific job.
Return only valid JSON. Do not include markdown, explanations, or prose.

Rules:
- You must never invent IDs or skill labels.
- Use only IDs and labels present in the provided allowed lists.
- If a section should include everything, you may omit that section's selection key.
- section_order may only use: Experience, Projects, Education, Skills.
- bullet_overrides keys must be valid entry IDs from experience/project/education.
- Keep bullet_overrides concise and tailored to the job description.
""".strip()


def build_selection_invocation(
    profile: Profile,
    job: Job,
    *,
    feedback_errors: Sequence[str] | None = None,
    max_job_chars: int = 8000,
) -> LlmInvocation:
    """
    Build provider-agnostic prompt payload for selection generation.

    :param profile: Parsed profile input.
    :type profile: tailorcv.schema.profile_schema.Profile
    :param job: Parsed job description.
    :type job: tailorcv.schema.job_schema.Job
    :param feedback_errors: Optional validation/provider feedback from prior attempts.
    :type feedback_errors: collections.abc.Sequence[str] | None
    :param max_job_chars: Maximum cleaned job text chars to include in the prompt.
    :type max_job_chars: int
    :return: Prompt invocation payload.
    :rtype: tailorcv.llm.base.LlmInvocation
    """
    payload: dict[str, Any] = {
        "task": (
            "Select the most relevant profile items for this job and return JSON matching "
            "LlmSelectionPlan."
        ),
        "allowed_values": _allowed_values(profile),
        "profile": _profile_payload(profile),
        "job": {
            "keywords": job.keywords[:40],
            "cleaned_text_excerpt": job.cleaned_text[:max_job_chars],
        },
        "output_template": {
            "selected_experience_ids": ["exp_id_1"],
            "selected_project_ids": ["proj_id_1"],
            "selected_education_ids": ["edu_id_1"],
            "selected_skill_labels": ["Languages"],
            "bullet_overrides": {"exp_id_1": ["Optional rewritten bullet"]},
            "section_order": ["Experience", "Projects", "Education", "Skills"],
        },
    }

    if feedback_errors:
        payload["retry_feedback"] = list(feedback_errors)

    return LlmInvocation(
        system_prompt=_SYSTEM_PROMPT,
        user_prompt=json.dumps(payload, indent=2, ensure_ascii=True),
    )


def _allowed_values(profile: Profile) -> dict[str, list[str]]:
    return {
        "experience_ids": [e.id for e in profile.experience if e.id],
        "project_ids": [p.id for p in profile.projects if p.id],
        "education_ids": [e.id for e in profile.education if e.id],
        "skill_labels": [s.label for s in profile.skills],
        "section_order_titles": ["Experience", "Projects", "Education", "Skills"],
    }


def _profile_payload(profile: Profile) -> dict[str, Any]:
    return {
        "meta": {
            "name": profile.meta.name,
            "headline": profile.meta.headline,
            "location": profile.meta.location,
        },
        "experience": [
            {
                "id": e.id,
                "company": e.company,
                "position": e.position,
                "summary": e.summary,
                "highlights": e.highlights,
                "tags": e.tags,
            }
            for e in profile.experience
        ],
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "summary": p.summary,
                "highlights": p.highlights,
                "tags": p.tags,
            }
            for p in profile.projects
        ],
        "education": [
            {
                "id": e.id,
                "institution": e.institution,
                "area": e.area,
                "degree": e.degree,
                "summary": e.summary,
                "highlights": e.highlights,
                "tags": e.tags,
            }
            for e in profile.education
        ],
        "skills": [
            {
                "label": s.label,
                "details": s.details,
            }
            for s in profile.skills
        ],
    }
