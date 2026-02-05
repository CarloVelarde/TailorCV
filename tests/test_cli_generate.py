from __future__ import annotations

from pathlib import Path

from rendercv.schema.yaml_reader import read_yaml
from typer.testing import CliRunner

from tailorcv.cli import app
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
