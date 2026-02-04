"""Manual smoke tests for TailorCV loaders and RenderCV validation."""

import argparse
from pathlib import Path

from rendercv.exception import RenderCVUserValidationError
from rendercv.schema.yaml_reader import read_yaml

from tailorcv.llm.selection_schema import SelectionLoadError, load_selection_plan
from tailorcv.loaders.job_loader import load_job
from tailorcv.loaders.profile_loader import load_profile
from tailorcv.mappers.rendercv_mapper import build_cv_dict
from tailorcv.validators.rendercv_validator import validate_rendercv_document
from tailorcv.validators.selection_validator import (
    SelectionValidationFailure,
    validate_selection_against_profile,
)


def _print_job_summary(job_path: Path) -> None:
    """
    Load a job file and print summary statistics.

    :param job_path: Path to a job description text file.
    :type job_path: pathlib.Path
    :return: None.
    :rtype: None
    """
    job = load_job(job_path)

    print("\n" + "=" * 80)
    print("JOB LOADER DEBUG OUTPUT")
    print("=" * 80)

    print(f"\nJob file: {job_path}")
    print(f"Raw text length:     {len(job.raw_text)} characters")
    print(f"Cleaned text length: {len(job.cleaned_text)} characters")

    reduction = 100 * (1 - len(job.cleaned_text) / max(len(job.raw_text), 1))
    print(f"Reduction:           {reduction:.1f}%")

    print("\nTop extracted keywords:")
    for i, kw in enumerate(job.keywords, start=1):
        print(f"{i:2d}. {kw}")

    print("\nCleaned text preview (first 500 chars):")
    print("-" * 80)
    print(job.cleaned_text[:500])
    print("-" * 80)


def _print_profile_summary(profile_path: Path) -> None:
    """
    Load a profile file and print summary statistics.

    :param profile_path: Path to a profile.yaml file.
    :type profile_path: pathlib.Path
    :return: None.
    :rtype: None
    """
    profile = load_profile(profile_path)

    print("\n" + "=" * 80)
    print("PROFILE LOADER DEBUG OUTPUT")
    print("=" * 80)

    print(f"\nProfile file: {profile_path}")
    print(f"Name: {profile.meta.name}")
    print(f"Education entries:   {len(profile.education)}")
    print(f"Experience entries:  {len(profile.experience)}")
    print(f"Project entries:     {len(profile.projects)}")
    print(f"Skill entries:       {len(profile.skills)}")
    print(f"Certifications:      {len(profile.certifications)}")
    print(f"Interests:           {len(profile.interests)}")


def _validate_rendercv_yaml(rendercv_path: Path) -> None:
    """
    Validate a RenderCV YAML file using official RenderCV models.

    :param rendercv_path: Path to a RenderCV YAML file.
    :type rendercv_path: pathlib.Path
    :return: None.
    :rtype: None
    :raises rendercv.exception.RenderCVUserValidationError: If validation fails.
    """
    print("\n" + "=" * 80)
    print("RENDERCV VALIDATION OUTPUT")
    print("=" * 80)

    data = read_yaml(rendercv_path)
    validate_rendercv_document(data, input_file_path=rendercv_path)
    print(f"\nRenderCV validation passed: {rendercv_path}")


def _print_selection_summary(selection_path: Path) -> None:
    """
    Load an LLM selection plan and print summary statistics.

    :param selection_path: Path to a selection JSON file.
    :type selection_path: pathlib.Path
    :return: None.
    :rtype: None
    :raises SelectionLoadError: If the selection file is invalid.
    """
    plan = load_selection_plan(selection_path)

    print("\n" + "=" * 80)
    print("LLM SELECTION PLAN OUTPUT")
    print("=" * 80)

    print(f"\nSelection file: {selection_path}")
    print(f"Experience IDs: {len(plan.selected_experience_ids)}")
    print(f"Project IDs:    {len(plan.selected_project_ids)}")
    print(f"Education IDs:  {len(plan.selected_education_ids)}")
    print(f"Skill labels:   {len(plan.selected_skill_labels)}")
    print(f"Overrides:      {len(plan.bullet_overrides)}")
    print(f"Section order:  {len(plan.section_order)}")


def _validate_selection_plan(profile_path: Path, selection_path: Path) -> None:
    """
    Validate a selection plan strictly against the profile.

    :param profile_path: Path to a profile.yaml file.
    :type profile_path: pathlib.Path
    :param selection_path: Path to a selection JSON file.
    :type selection_path: pathlib.Path
    :return: None.
    :rtype: None
    :raises SelectionValidationFailure: If strict validation fails.
    """
    profile = load_profile(profile_path)
    plan = load_selection_plan(selection_path)
    validate_selection_against_profile(profile, plan, strict=True)

    print("\n" + "=" * 80)
    print("SELECTION VALIDATION OUTPUT")
    print("=" * 80)
    print("\nSelection validation passed.")


def _print_mapper_preview(profile_path: Path, selection_path: Path) -> None:
    """
    Build a RenderCV cv dict and print a brief summary of sections.

    :param profile_path: Path to a profile.yaml file.
    :type profile_path: pathlib.Path
    :param selection_path: Path to a selection JSON file.
    :type selection_path: pathlib.Path
    :return: None.
    :rtype: None
    :raises SelectionLoadError: If the selection file is invalid.
    """
    profile = load_profile(profile_path)
    plan = load_selection_plan(selection_path)
    cv_doc = build_cv_dict(profile, plan)

    sections = cv_doc.get("cv", {}).get("sections", {})
    print("\n" + "=" * 80)
    print("MAPPER PREVIEW OUTPUT")
    print("=" * 80)
    print(f"\nSections: {list(sections.keys())}")
    for name, entries in sections.items():
        print(f"- {name}: {len(entries)} entries")


def main() -> int:
    """
    Run the smoke test entrypoint.

    :return: Exit status (0 for success, 1 for failure).
    :rtype: int
    """
    parser = argparse.ArgumentParser(
        description="Manual smoke test for TailorCV loaders and RenderCV validation."
    )
    parser.add_argument(
        "--job",
        type=Path,
        default=Path("tailorcv/examples/jobs/sample_job.txt"),
        help="Path to a job description .txt file.",
    )
    parser.add_argument(
        "--profile",
        type=Path,
        default=Path("tailorcv/examples/sample_input_profile.yaml"),
        help="Path to a profile.yaml file.",
    )
    parser.add_argument(
        "--rendercv",
        type=Path,
        default=Path("tailorcv/examples/rendercv_input_profile.yaml"),
        help="Path to a RenderCV YAML file to validate.",
    )
    parser.add_argument(
        "--selection",
        type=Path,
        default=Path("tailorcv/examples/llm_selection_example.json"),
        help="Path to a selection JSON file to validate.",
    )
    parser.add_argument(
        "--skip-job",
        action="store_true",
        help="Skip job loader debug output.",
    )
    parser.add_argument(
        "--skip-profile",
        action="store_true",
        help="Skip profile loader debug output.",
    )
    parser.add_argument(
        "--skip-rendercv",
        action="store_true",
        help="Skip RenderCV validation output.",
    )
    parser.add_argument(
        "--skip-selection",
        action="store_true",
        help="Skip LLM selection plan validation output.",
    )
    parser.add_argument(
        "--skip-mapper",
        action="store_true",
        help="Skip mapper preview output.",
    )
    parser.add_argument(
        "--skip-selection-validation",
        action="store_true",
        help="Skip strict selection validation output.",
    )
    args = parser.parse_args()

    try:
        if not args.skip_job:
            _print_job_summary(args.job)
        if not args.skip_profile:
            _print_profile_summary(args.profile)
        if not args.skip_selection:
            _print_selection_summary(args.selection)
        if not args.skip_selection_validation:
            _validate_selection_plan(args.profile, args.selection)
        if not args.skip_mapper:
            _print_mapper_preview(args.profile, args.selection)
        if not args.skip_rendercv:
            _validate_rendercv_yaml(args.rendercv)
    except RenderCVUserValidationError as exc:
        print("\nRenderCV validation failed:")
        for error in exc.validation_errors:
            location = ".".join(error.location)
            message = error.message
            print(f"- {location}: {message}")
        return 1
    except SelectionLoadError as exc:
        print(f"\nSelection validation failed: {exc}")
        return 1
    except SelectionValidationFailure as exc:
        print("\nSelection validation failed:")
        for error in exc.errors:
            print(f"- {error.message}")
        return 1
    except Exception as exc:  # pragma: no cover - debug only
        print(f"\nError: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
