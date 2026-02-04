"""CLI command wrapper for the TailorCV debug pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from tailorcv.debug import main as debug_main


def debug(
    job: Optional[Path] = typer.Option(
        None,
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to a job description .txt file.",
    ),
    profile: Optional[Path] = typer.Option(
        None,
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to a profile.yaml file.",
    ),
    rendercv: Optional[Path] = typer.Option(
        None,
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to a RenderCV YAML file to validate.",
    ),
    selection: Optional[Path] = typer.Option(
        None,
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to a selection JSON file to validate.",
    ),
    skip_job: bool = typer.Option(False, help="Skip job loader debug output."),
    skip_profile: bool = typer.Option(False, help="Skip profile loader debug output."),
    skip_selection: bool = typer.Option(False, help="Skip LLM selection plan validation output."),
    skip_selection_validation: bool = typer.Option(
        False, help="Skip strict selection validation output."
    ),
    skip_mapper: bool = typer.Option(False, help="Skip mapper preview output."),
    skip_assembly: bool = typer.Option(False, help="Skip document assembly output."),
    skip_rendercv: bool = typer.Option(False, help="Skip RenderCV validation output."),
) -> None:
    """
    Run the debug pipeline with optional overrides.

    :param job: Path to a job description .txt file.
    :type job: pathlib.Path | None
    :param profile: Path to a profile.yaml file.
    :type profile: pathlib.Path | None
    :param rendercv: Path to a RenderCV YAML file.
    :type rendercv: pathlib.Path | None
    :param selection: Path to a selection JSON file.
    :type selection: pathlib.Path | None
    :param skip_job: Skip job loader output.
    :type skip_job: bool
    :param skip_profile: Skip profile loader output.
    :type skip_profile: bool
    :param skip_selection: Skip selection plan output.
    :type skip_selection: bool
    :param skip_selection_validation: Skip strict selection validation.
    :type skip_selection_validation: bool
    :param skip_mapper: Skip mapper preview output.
    :type skip_mapper: bool
    :param skip_assembly: Skip document assembly output.
    :type skip_assembly: bool
    :param skip_rendercv: Skip RenderCV validation output.
    :type skip_rendercv: bool
    :return: None.
    :rtype: None
    """
    argv: list[str] = []

    if job is not None:
        argv += ["--job", str(job)]
    if profile is not None:
        argv += ["--profile", str(profile)]
    if rendercv is not None:
        argv += ["--rendercv", str(rendercv)]
    if selection is not None:
        argv += ["--selection", str(selection)]

    if skip_job:
        argv.append("--skip-job")
    if skip_profile:
        argv.append("--skip-profile")
    if skip_selection:
        argv.append("--skip-selection")
    if skip_selection_validation:
        argv.append("--skip-selection-validation")
    if skip_mapper:
        argv.append("--skip-mapper")
    if skip_assembly:
        argv.append("--skip-assembly")
    if skip_rendercv:
        argv.append("--skip-rendercv")

    raise SystemExit(debug_main(argv))
