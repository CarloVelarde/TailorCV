"""Validation helpers that use official RenderCV models."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import pydantic
from rendercv.exception import RenderCVUserValidationError
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.models.validation_context import ValidationContext
from rendercv.schema.pydantic_error_handling import parse_validation_errors
from ruamel.yaml.comments import CommentedMap


def validate_rendercv_document(
    data: Mapping[str, Any],
    *,
    input_file_path: str | Path | None = None,
) -> RenderCVModel:
    """
    Validate a RenderCV document using RenderCV's official Pydantic models.

    This enforces schema correctness for user-supplied design/locale/settings
    blocks and prevents drift between TailorCV's internal schema and RenderCV.

    :param data: RenderCV document data as a mapping.
    :type data: collections.abc.Mapping[str, typing.Any]
    :param input_file_path: Optional file path for relative resolution context.
    :type input_file_path: str | pathlib.Path | None
    :return: Validated RenderCV model instance.
    :rtype: rendercv.schema.models.rendercv_model.RenderCVModel
    :raises rendercv.exception.RenderCVUserValidationError: On schema validation errors.
    """
    resolved_path = Path(input_file_path) if input_file_path else None
    context = ValidationContext(
        input_file_path=resolved_path,
        current_date=data.get("settings", {}).get("current_date") if data else None,
    )

    try:
        return RenderCVModel.model_validate(data, context={"context": context})
    except pydantic.ValidationError as exc:
        error_input = data if isinstance(data, CommentedMap) else dict(data)
        errors = parse_validation_errors(exc, error_input)
        raise RenderCVUserValidationError(errors) from exc
