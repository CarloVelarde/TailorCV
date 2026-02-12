from __future__ import annotations

from pathlib import Path

import pytest

from tailorcv.app.pipeline import build_rendercv_document
from tailorcv.llm.selection_schema import LlmSelectionPlan


def test_build_rendercv_document_pipeline(
    profile_valid_path: Path,
    job_min_path: Path,
    selection_valid_path: Path,
) -> None:
    doc = build_rendercv_document(
        profile_path=profile_valid_path,
        job_path=job_min_path,
        selection_path=selection_valid_path,
    )

    assert {"cv", "design", "locale", "settings"} <= set(doc.keys())
    assert "sections" in doc["cv"]


def test_build_rendercv_document_uses_selector_when_selection_missing(
    profile_valid_path: Path,
    job_min_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: dict[str, bool] = {"selector_called": False}

    def fake_generate_selection_plan(
        profile: object, job: object, options: object = None
    ) -> object:
        called["selector_called"] = True
        return LlmSelectionPlan(
            selected_experience_ids=["exp_1"],
            selected_project_ids=["proj_1"],
            selected_education_ids=["edu_1"],
            selected_skill_labels=["Languages"],
        )

    monkeypatch.setattr(
        "tailorcv.app.pipeline.generate_selection_plan", fake_generate_selection_plan
    )

    doc = build_rendercv_document(
        profile_path=profile_valid_path,
        job_path=job_min_path,
    )

    assert called["selector_called"] is True
    assert {"cv", "design", "locale", "settings"} <= set(doc.keys())
