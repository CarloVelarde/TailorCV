"""LLM selection output contract for the MVP pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel, Field


class SelectionLoadError(Exception):
    """Raised when a selection JSON file cannot be loaded or validated."""


class LlmSelectionPlan(BaseModel):
    """
    Structured LLM output describing which profile items to include.

    :param selected_experience_ids: Experience entry IDs to include.
    :type selected_experience_ids: list[str]
    :param selected_project_ids: Project entry IDs to include.
    :type selected_project_ids: list[str]
    :param selected_education_ids: Education entry IDs to include.
    :type selected_education_ids: list[str]
    :param selected_skill_labels: Skill section labels to include.
    :type selected_skill_labels: list[str]
    :param bullet_overrides: Optional rewritten bullets keyed by entry ID.
    :type bullet_overrides: dict[str, list[str]]
    :param section_order: Optional preferred section ordering.
    :type section_order: list[str]
    """

    selected_experience_ids: List[str] = Field(default_factory=list)
    selected_project_ids: List[str] = Field(default_factory=list)
    selected_education_ids: List[str] = Field(default_factory=list)
    selected_skill_labels: List[str] = Field(default_factory=list)
    bullet_overrides: Dict[str, List[str]] = Field(default_factory=dict)
    section_order: List[str] = Field(default_factory=list)


def load_selection_plan(selection_path: str | Path) -> LlmSelectionPlan:
    """
    Load and validate a selection plan from a JSON file.

    :param selection_path: Path to a JSON file containing the selection plan.
    :type selection_path: str | pathlib.Path
    :return: Validated LLM selection plan.
    :rtype: LlmSelectionPlan
    :raises SelectionLoadError: If the file cannot be read or validated.
    """
    selection_path = Path(selection_path)
    if not selection_path.exists():
        raise SelectionLoadError(f"Selection file not found: {selection_path}")

    try:
        raw = selection_path.read_text(encoding="utf-8")
    except Exception as exc:
        raise SelectionLoadError(f"Failed to read selection file: {exc}") from exc

    try:
        payload = json.loads(raw)
    except Exception as exc:
        raise SelectionLoadError(f"Selection file is not valid JSON: {exc}") from exc

    try:
        return LlmSelectionPlan.model_validate(payload)
    except Exception as exc:
        raise SelectionLoadError(f"Selection schema validation failed: {exc}") from exc
