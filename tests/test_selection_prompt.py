from __future__ import annotations

from pathlib import Path

from tailorcv.llm.selection_prompt import build_selection_invocation
from tailorcv.loaders.job_loader import load_job
from tailorcv.loaders.profile_loader import load_profile


def test_build_selection_invocation_contains_allowed_values(
    profile_valid_path: Path,
    job_min_path: Path,
) -> None:
    profile = load_profile(profile_valid_path)
    job = load_job(job_min_path)

    invocation = build_selection_invocation(profile, job)

    assert "never invent IDs or skill labels" in invocation.system_prompt
    assert '"experience_ids": [' in invocation.user_prompt
    assert '"exp_1"' in invocation.user_prompt
    assert '"skill_labels": [' in invocation.user_prompt
    assert '"Languages"' in invocation.user_prompt


def test_build_selection_invocation_includes_retry_feedback(
    profile_valid_path: Path,
    job_min_path: Path,
) -> None:
    profile = load_profile(profile_valid_path)
    job = load_job(job_min_path)

    invocation = build_selection_invocation(
        profile,
        job,
        feedback_errors=["Unknown experience id: 'bad_id'."],
    )

    assert '"retry_feedback"' in invocation.user_prompt
    assert "bad_id" in invocation.user_prompt
