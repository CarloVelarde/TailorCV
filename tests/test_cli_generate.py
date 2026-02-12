from __future__ import annotations

from pathlib import Path

import pytest
from rendercv.schema.yaml_reader import read_yaml
from typer.testing import CliRunner

from tailorcv.cli import app
from tailorcv.llm.selection_schema import LlmSelectionPlan
from tailorcv.validators.rendercv_validator import validate_rendercv_document


def test_cli_generate_integration(
    tmp_path: Path,
    profile_valid_path: Path,
    job_min_path: Path,
    selection_valid_path: Path,
) -> None:
    out_path = tmp_path / "out.yaml"
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "generate",
            "--profile",
            str(profile_valid_path),
            "--job",
            str(job_min_path),
            "--selection",
            str(selection_valid_path),
            "--out",
            str(out_path),
        ],
    )
    assert result.exit_code == 0, result.output
    assert out_path.exists()

    data = read_yaml(out_path)
    validate_rendercv_document(data)


def test_cli_generate_defaults_to_llm_selection(
    tmp_path: Path,
    profile_valid_path: Path,
    job_min_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    out_path = tmp_path / "out_llm.yaml"
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

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "generate",
            "--profile",
            str(profile_valid_path),
            "--job",
            str(job_min_path),
            "--out",
            str(out_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert out_path.exists()
    assert called["selector_called"] is True

    data = read_yaml(out_path)
    validate_rendercv_document(data)


def test_cli_generate_manual_selection_skips_selector(
    tmp_path: Path,
    profile_valid_path: Path,
    job_min_path: Path,
    selection_valid_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    out_path = tmp_path / "out_manual.yaml"

    def fail_if_called(*args: object, **kwargs: object) -> object:
        raise AssertionError("Selector should not be called when --selection is provided.")

    monkeypatch.setattr("tailorcv.app.pipeline.generate_selection_plan", fail_if_called)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "generate",
            "--profile",
            str(profile_valid_path),
            "--job",
            str(job_min_path),
            "--selection",
            str(selection_valid_path),
            "--out",
            str(out_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert out_path.exists()
