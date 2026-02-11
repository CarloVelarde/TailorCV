"""CLI command for generating RenderCV YAML from profile + job + selection."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import ruamel.yaml
import typer
from rendercv.exception import RenderCVUserValidationError
from rendercv.schema.yaml_reader import read_yaml

from tailorcv.app.pipeline import build_rendercv_document
from tailorcv.llm.selection_schema import SelectionLoadError
from tailorcv.loaders.job_loader import JobLoadError
from tailorcv.loaders.profile_loader import ProfileLoadError
from tailorcv.validators.selection_validator import SelectionValidationFailure


class GenerateError(ValueError):
    """Raised when CLI generation fails."""


def generate(
    profile: Path = typer.Option(
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to profile.yaml.",
    ),
    job: Path = typer.Option(
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to job.txt.",
    ),
    selection: Path = typer.Option(
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to selection JSON (MVP/testing; LLM will replace).",
    ),
    out: Path = typer.Option(
        ...,
        help="Output file path or directory for the RenderCV YAML file.",
    ),
    design: Path | None = typer.Option(
        None,
        exists=True,
        dir_okay=False,
        readable=True,
        help="Optional design override YAML file.",
    ),
    locale: Path | None = typer.Option(
        None,
        exists=True,
        dir_okay=False,
        readable=True,
        help="Optional locale override YAML file.",
    ),
    settings: Path | None = typer.Option(
        None,
        exists=True,
        dir_okay=False,
        readable=True,
        help="Optional settings override YAML file.",
    ),
) -> None:
    """
    Generate a RenderCV YAML file from profile, job, and selection inputs.

    :param profile: Path to profile.yaml.
    :type profile: pathlib.Path
    :param job: Path to job.txt.
    :type job: pathlib.Path
    :param selection: Path to selection JSON file.
    :type selection: pathlib.Path
    :param out: Output file path or directory.
    :type out: pathlib.Path
    :param design: Optional design override YAML file.
    :type design: pathlib.Path | None
    :param locale: Optional locale override YAML file.
    :type locale: pathlib.Path | None
    :param settings: Optional settings override YAML file.
    :type settings: pathlib.Path | None
    :return: None.
    :rtype: None
    """
    try:
        typer.secho(
            "Note: --selection is an MVP/testing input and will become optional "
            "once LLM integration is added.",
            fg=typer.colors.YELLOW,
            err=True,
        )
        design_block = _load_optional_block(design, "design")
        locale_block = _load_optional_block(locale, "locale")
        settings_block = _load_optional_block(settings, "settings")

        document = build_rendercv_document(
            profile_path=profile,
            job_path=job,
            selection_path=selection,
            design=design_block,
            locale=locale_block,
            settings=settings_block,
        )
        out_path = _resolve_out_path(out)
        _write_yaml(document, out_path)

        print(f"RenderCV YAML written to: {out_path}")
    except (
        ProfileLoadError,
        JobLoadError,
        SelectionLoadError,
        SelectionValidationFailure,
        RenderCVUserValidationError,
        GenerateError,
    ) as exc:
        _print_error(exc)
        raise typer.Exit(code=1)


def _load_optional_block(path: Path | None, key: str) -> Mapping[str, Any] | None:
    """
    Load an optional YAML block from a file path.

    Accepts either a top-level block (e.g., {"design": {...}}) or a raw block
    mapping. Returns None when no path is provided.

    :param path: Path to a YAML file.
    :type path: pathlib.Path | None
    :param key: Expected top-level key when a full document is provided.
    :type key: str
    :return: Parsed mapping or None.
    :rtype: collections.abc.Mapping[str, typing.Any] | None
    :raises GenerateError: If the file cannot be read or is not a mapping.
    """
    if path is None:
        return None

    data = read_yaml(path)
    if not isinstance(data, dict):
        raise GenerateError(f"{key} file must be a mapping: {path}")

    if key in data and isinstance(data[key], dict):
        return data[key]
    if key in data:
        raise GenerateError(f"{key} block must be a mapping: {path}")
    return data


def _resolve_out_path(out_path: Path) -> Path:
    """
    Resolve the output file path.

    If the path is a directory, write to ``rendercv_output.yaml`` within it.

    :param out_path: Output path provided by the user.
    :type out_path: pathlib.Path
    :return: Resolved file path.
    :rtype: pathlib.Path
    """
    if out_path.exists() and out_path.is_dir():
        return out_path / "rendercv_output.yaml"
    return out_path


def _write_yaml(document: Mapping[str, Any], out_path: Path) -> None:
    """
    Write a RenderCV document to a YAML file.

    :param document: RenderCV document dictionary.
    :type document: collections.abc.Mapping[str, typing.Any]
    :param out_path: Output path for the YAML file.
    :type out_path: pathlib.Path
    :return: None.
    :rtype: None
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    with out_path.open("w", encoding="utf-8") as f:
        yaml.dump(document, f)


def _print_error(exc: Exception) -> None:
    """
    Print a user-facing error message.

    :param exc: Exception to display.
    :type exc: Exception
    :return: None.
    :rtype: None
    """
    if isinstance(exc, SelectionValidationFailure):
        print("Selection validation failed:")
        for error in exc.errors:
            print(f"- {error.message}")
        return
    if isinstance(exc, RenderCVUserValidationError):
        print("RenderCV validation failed:")
        for error in exc.validation_errors:
            location = ".".join(error.location)
            print(f"- {location}: {error.message}")
        return
    print(f"Error: {exc}")
