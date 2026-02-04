"""Strict validation for LLM selection plans against a profile."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from tailorcv.llm.selection_schema import LlmSelectionPlan
from tailorcv.schema.profile_schema import Profile


@dataclass(frozen=True)
class SelectionValidationError:
    """Represents a single selection validation error."""

    message: str


class SelectionValidationFailure(ValueError):
    """Raised when a selection plan fails strict validation."""

    def __init__(self, errors: List[SelectionValidationError]) -> None:
        super().__init__("Selection plan failed validation.")
        self.errors = errors


def validate_selection_against_profile(
    profile: Profile,
    plan: LlmSelectionPlan,
    *,
    strict: bool = True,
) -> None:
    """
    Validate that a selection plan only references items in the profile.

    In strict mode, any invalid ID, unknown label, or empty selection that
    produces no sections raises a SelectionValidationFailure.

    :param profile: Parsed profile input.
    :type profile: tailorcv.schema.profile_schema.Profile
    :param plan: LLM selection plan.
    :type plan: tailorcv.llm.selection_schema.LlmSelectionPlan
    :param strict: When True, raise on any validation error.
    :type strict: bool
    :return: None.
    :rtype: None
    :raises SelectionValidationFailure: If validation errors are found.
    """
    errors: List[SelectionValidationError] = []

    _validate_ids(
        errors,
        provided=plan.selected_experience_ids,
        known=[e.id for e in profile.experience],
        label="experience",
    )
    _validate_ids(
        errors,
        provided=plan.selected_project_ids,
        known=[p.id for p in profile.projects],
        label="projects",
    )
    _validate_ids(
        errors,
        provided=plan.selected_education_ids,
        known=[e.id for e in profile.education],
        label="education",
    )

    _validate_labels(
        errors,
        provided=plan.selected_skill_labels,
        known=[s.label for s in profile.skills],
        label="skills",
    )

    _validate_bullet_overrides(errors, plan, profile)
    _validate_non_empty_selection(errors, plan, profile)

    if errors and strict:
        raise SelectionValidationFailure(errors)


def _validate_ids(
    errors: List[SelectionValidationError],
    *,
    provided: Iterable[str],
    known: Iterable[str | None],
    label: str,
) -> None:
    known_ids = {k for k in known if k}
    for item_id in provided:
        if item_id not in known_ids:
            errors.append(
                SelectionValidationError(
                    message=f"Unknown {label} id: '{item_id}'.",
                )
            )


def _validate_labels(
    errors: List[SelectionValidationError],
    *,
    provided: Iterable[str],
    known: Iterable[str],
    label: str,
) -> None:
    known_labels = set(known)
    for item_label in provided:
        if item_label not in known_labels:
            errors.append(
                SelectionValidationError(
                    message=f"Unknown {label} label: '{item_label}'.",
                )
            )


def _validate_bullet_overrides(
    errors: List[SelectionValidationError],
    plan: LlmSelectionPlan,
    profile: Profile,
) -> None:
    valid_ids = {
        *(e.id for e in profile.experience if e.id),
        *(p.id for p in profile.projects if p.id),
        *(e.id for e in profile.education if e.id),
    }
    for entry_id in plan.bullet_overrides:
        if entry_id not in valid_ids:
            errors.append(
                SelectionValidationError(
                    message=f"Unknown bullet_overrides id: '{entry_id}'.",
                )
            )


def _validate_non_empty_selection(
    errors: List[SelectionValidationError],
    plan: LlmSelectionPlan,
    profile: Profile,
) -> None:
    selected_experience = plan.selected_experience_ids or [e.id for e in profile.experience]
    selected_projects = plan.selected_project_ids or [p.id for p in profile.projects]
    selected_education = plan.selected_education_ids or [e.id for e in profile.education]
    selected_skills = plan.selected_skill_labels or [s.label for s in profile.skills]

    has_any = any(
        [
            selected_experience,
            selected_projects,
            selected_education,
            selected_skills,
        ]
    )
    if not has_any:
        errors.append(
            SelectionValidationError(
                message="Selection plan results in an empty resume.",
            )
        )
