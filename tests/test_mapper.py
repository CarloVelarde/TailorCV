from __future__ import annotations

from pathlib import Path

from tailorcv.llm.selection_schema import load_selection_plan
from tailorcv.loaders.profile_loader import load_profile
from tailorcv.mappers.rendercv_mapper import build_cv_dict


def test_build_cv_dict_structure(
    profile_valid_path: Path,
    selection_valid_path: Path,
) -> None:
    profile = load_profile(profile_valid_path)
    plan = load_selection_plan(selection_valid_path)
    cv_doc = build_cv_dict(profile, plan)

    sections = cv_doc["cv"]["sections"]
    assert set(sections.keys()) == {"Experience", "Projects", "Education", "Skills"}


def test_build_cv_dict_omits_empty_highlights(
    profile_valid_path: Path,
    selection_valid_path: Path,
) -> None:
    profile = load_profile(profile_valid_path)
    plan = load_selection_plan(selection_valid_path)
    cv_doc = build_cv_dict(profile, plan)

    education_entry = cv_doc["cv"]["sections"]["Education"][0]
    assert "highlights" not in education_entry


def test_build_cv_dict_uses_bullet_overrides(
    profile_valid_path: Path,
    selection_overrides_path: Path,
) -> None:
    profile = load_profile(profile_valid_path)
    plan = load_selection_plan(selection_overrides_path)
    cv_doc = build_cv_dict(profile, plan)

    exp_entry = cv_doc["cv"]["sections"]["Experience"][0]
    assert exp_entry["highlights"] == ["Rewritten bullet from override."]
