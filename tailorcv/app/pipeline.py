"""Application pipeline orchestration for TailorCV generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from tailorcv.assemblers.rendercv_document import assemble_rendercv_document
from tailorcv.llm.selection_schema import load_selection_plan
from tailorcv.llm.selector import SelectionGenerationOptions, generate_selection_plan
from tailorcv.loaders.job_loader import load_job
from tailorcv.loaders.profile_loader import load_profile
from tailorcv.mappers.rendercv_mapper import build_cv_dict
from tailorcv.validators.rendercv_validator import validate_rendercv_document
from tailorcv.validators.selection_validator import validate_selection_against_profile


def build_rendercv_document(
    *,
    profile_path: Path,
    job_path: Path,
    selection_path: Path | None = None,
    llm_options: SelectionGenerationOptions | None = None,
    design: Mapping[str, Any] | None = None,
    locale: Mapping[str, Any] | None = None,
    settings: Mapping[str, Any] | None = None,
) -> Mapping[str, Any]:
    """
    Build and validate a RenderCV document from input files and optional overrides.

    :param profile_path: Path to profile.yaml.
    :type profile_path: pathlib.Path
    :param job_path: Path to job.txt.
    :type job_path: pathlib.Path
    :param selection_path: Optional path to selection.json manual override.
    :type selection_path: pathlib.Path | None
    :param llm_options: Optional LLM generation runtime overrides.
    :type llm_options: tailorcv.llm.selector.SelectionGenerationOptions | None
    :param design: Optional design block override.
    :type design: collections.abc.Mapping[str, typing.Any] | None
    :param locale: Optional locale block override.
    :type locale: collections.abc.Mapping[str, typing.Any] | None
    :param settings: Optional settings block override.
    :type settings: collections.abc.Mapping[str, typing.Any] | None
    :return: Validated RenderCV document dictionary.
    :rtype: collections.abc.Mapping[str, typing.Any]
    :raises ProfileLoadError: If profile loading fails.
    :raises JobLoadError: If job loading fails.
    :raises SelectionLoadError: If manual selection loading fails.
    :raises SelectionValidationFailure: If strict selection validation fails.
    :raises rendercv.exception.RenderCVUserValidationError: If RenderCV validation fails.
    """
    profile_obj = load_profile(profile_path)
    job = load_job(job_path)

    if selection_path is not None:
        plan = load_selection_plan(selection_path)
    else:
        plan = generate_selection_plan(profile_obj, job, options=llm_options)

    validate_selection_against_profile(profile_obj, plan, strict=True)

    cv_doc = build_cv_dict(profile_obj, plan)
    document = assemble_rendercv_document(
        cv_doc,
        design=design,
        locale=locale,
        settings=settings,
    )
    validate_rendercv_document(document)
    return document
