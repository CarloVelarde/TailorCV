from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pytest

from tailorcv.llm.base import LlmInvocation, StructuredLlmProvider
from tailorcv.llm.selection_schema import LlmSelectionPlan
from tailorcv.llm.selector import (
    SelectionGenerationFailure,
    SelectionGenerationOptions,
    generate_selection_plan,
)
from tailorcv.loaders.job_loader import load_job
from tailorcv.loaders.profile_loader import load_profile


class _FakeProvider(StructuredLlmProvider):
    provider_name = "fake"
    model = "fake-model"

    def __init__(self, outputs: Sequence[LlmSelectionPlan]) -> None:
        self._outputs = list(outputs)
        self.invocations: list[LlmInvocation] = []

    def generate_structured(
        self,
        *,
        invocation: LlmInvocation,
        schema: type[LlmSelectionPlan],
    ) -> LlmSelectionPlan:
        self.invocations.append(invocation)
        if not self._outputs:
            raise RuntimeError("No more fake outputs.")
        return self._outputs.pop(0)


def test_generate_selection_plan_success_first_attempt(
    profile_valid_path: Path,
    job_min_path: Path,
) -> None:
    profile = load_profile(profile_valid_path)
    job = load_job(job_min_path)
    provider = _FakeProvider(
        [
            LlmSelectionPlan(
                selected_experience_ids=["exp_1"],
                selected_project_ids=["proj_1"],
                selected_education_ids=["edu_1"],
                selected_skill_labels=["Languages"],
            )
        ]
    )

    plan = generate_selection_plan(profile, job, provider_client=provider)
    assert plan.selected_experience_ids == ["exp_1"]
    assert len(provider.invocations) == 1


def test_generate_selection_plan_retries_on_validation_feedback(
    profile_valid_path: Path,
    job_min_path: Path,
) -> None:
    profile = load_profile(profile_valid_path)
    job = load_job(job_min_path)
    provider = _FakeProvider(
        [
            LlmSelectionPlan(
                selected_experience_ids=["bad_id"],
            ),
            LlmSelectionPlan(
                selected_experience_ids=["exp_1"],
                selected_project_ids=["proj_1"],
                selected_education_ids=["edu_1"],
                selected_skill_labels=["Languages"],
            ),
        ]
    )

    plan = generate_selection_plan(
        profile,
        job,
        options=SelectionGenerationOptions(max_attempts=2),
        provider_client=provider,
    )

    assert plan.selected_experience_ids == ["exp_1"]
    assert len(provider.invocations) == 2
    assert "Unknown experience id" in provider.invocations[1].user_prompt


def test_generate_selection_plan_fails_after_max_attempts(
    profile_valid_path: Path,
    job_min_path: Path,
) -> None:
    profile = load_profile(profile_valid_path)
    job = load_job(job_min_path)
    provider = _FakeProvider(
        [
            LlmSelectionPlan(selected_experience_ids=["bad_1"]),
            LlmSelectionPlan(selected_experience_ids=["bad_2"]),
        ]
    )

    with pytest.raises(SelectionGenerationFailure) as exc:
        generate_selection_plan(
            profile,
            job,
            options=SelectionGenerationOptions(max_attempts=2),
            provider_client=provider,
        )

    assert len(exc.value.errors) == 2
    assert "attempt 1" in str(exc.value)


def test_generate_selection_plan_rejects_invalid_max_attempts(
    profile_valid_path: Path,
    job_min_path: Path,
) -> None:
    profile = load_profile(profile_valid_path)
    job = load_job(job_min_path)
    provider = _FakeProvider(
        [
            LlmSelectionPlan(
                selected_experience_ids=["exp_1"],
            )
        ]
    )

    with pytest.raises(ValueError) as exc:
        generate_selection_plan(
            profile,
            job,
            options=SelectionGenerationOptions(max_attempts=0),
            provider_client=provider,
        )

    assert "max_attempts" in str(exc.value)
