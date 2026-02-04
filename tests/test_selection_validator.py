from __future__ import annotations

from pathlib import Path

import pytest

from tailorcv.llm.selection_schema import load_selection_plan
from tailorcv.loaders.profile_loader import load_profile
from tailorcv.validators.selection_validator import (
    SelectionValidationFailure,
    validate_selection_against_profile,
)


def test_selection_validator_unknown_id(
    profile_valid_path: Path,
    selection_invalid_id_path: Path,
) -> None:
    profile = load_profile(profile_valid_path)
    plan = load_selection_plan(selection_invalid_id_path)
    with pytest.raises(SelectionValidationFailure) as exc:
        validate_selection_against_profile(profile, plan, strict=True)
    assert any("unknown experience id" in e.message.lower() for e in exc.value.errors)


def test_selection_validator_empty_resume(
    profile_empty_path: Path,
    selection_empty_path: Path,
) -> None:
    profile = load_profile(profile_empty_path)
    plan = load_selection_plan(selection_empty_path)
    with pytest.raises(SelectionValidationFailure) as exc:
        validate_selection_against_profile(profile, plan, strict=True)
    assert any("empty resume" in e.message.lower() for e in exc.value.errors)
