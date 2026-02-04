"""CLI entrypoint for generating RenderCV YAML from profile + job + selection."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Mapping

import ruamel.yaml
from rendercv.exception import RenderCVUserValidationError
from rendercv.schema.yaml_reader import read_yaml

from tailorcv.assemblers.rendercv_document import assemble_rendercv_document
from tailorcv.llm.selection_schema import SelectionLoadError, load_selection_plan
from tailorcv.loaders.job_loader import JobLoadError, load_job
from tailorcv.loaders.profile_loader import ProfileLoadError, load_profile
from tailorcv.mappers.rendercv_mapper import build_cv_dict
from tailorcv.validators.rendercv_validator import validate_rendercv_document
from tailorcv.validators.selection_validator import (
    SelectionValidationFailure,
    validate_selection_against_profile,
)


class GenerateError(ValueError):
    """Raised when CLI generation fails."""


def main(argv: list[str] | None = None) -> int:
    """
    Generate a RenderCV YAML file from profile, job, and selection inputs.

    :param argv: Optional argument list for CLI parsing.
    :type argv: list[str] | None
    :return: Exit status (0 for success, 1 for failure).
    :rtype: int
    """
    parser = argparse.ArgumentParser(
        description="Generate RenderCV YAML from profile, job, and LLM selection."
    )
    parser.add_argument(
        "--profile",
        type=Path,
        required=True,
        help="Path to profile.yaml.",
    )
    parser.add_argument(
        "--job",
        type=Path,
        required=True,
        help="Path to job.txt.",
    )
    parser.add_argument(
        "--selection",
        type=Path,
        required=True,
        help="Path to LLM selection JSON file.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output file path (or directory) for the RenderCV YAML file.",
    )
    parser.add_argument(
        "--design",
        type=Path,
        help="Optional design override YAML file.",
    )
    parser.add_argument(
        "--locale",
        type=Path,
        help="Optional locale override YAML file.",
    )
    parser.add_argument(
        "--settings",
        type=Path,
        help="Optional settings override YAML file.",
    )
    args = parser.parse_args(argv)

    try:
        profile = load_profile(args.profile)
        load_job(args.job)

        plan = load_selection_plan(args.selection)
        validate_selection_against_profile(profile, plan, strict=True)

        cv_doc = build_cv_dict(profile, plan)

        design = _load_optional_block(args.design, "design")
        locale = _load_optional_block(args.locale, "locale")
        settings = _load_optional_block(args.settings, "settings")

        document = assemble_rendercv_document(
            cv_doc,
            design=design,
            locale=locale,
            settings=settings,
        )

        validate_rendercv_document(document)
        out_path = _resolve_out_path(args.out)
        _write_yaml(document, out_path)

        print(f"RenderCV YAML written to: {out_path}")
        return 0
    except (
        ProfileLoadError,
        JobLoadError,
        SelectionLoadError,
        SelectionValidationFailure,
        RenderCVUserValidationError,
        GenerateError,
    ) as exc:
        _print_error(exc)
        return 1


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


if __name__ == "__main__":
    raise SystemExit(main())
