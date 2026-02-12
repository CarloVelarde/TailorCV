"""Selection generation service with strict validation and retry feedback."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from tailorcv.config.models import LlmProvider
from tailorcv.llm.base import (
    LlmProviderError,
    StructuredLlmProvider,
)
from tailorcv.llm.router import build_provider
from tailorcv.llm.runtime import LlmRuntimeConfigError, resolve_llm_runtime_config
from tailorcv.llm.selection_prompt import build_selection_invocation
from tailorcv.llm.selection_schema import LlmSelectionPlan
from tailorcv.schema.job_schema import Job
from tailorcv.schema.profile_schema import Profile
from tailorcv.validators.selection_validator import (
    SelectionValidationFailure,
    validate_selection_against_profile,
)


@dataclass(frozen=True)
class SelectionGenerationOptions:
    """
    Runtime options for LLM selection generation.

    :param provider: Optional provider override.
    :type provider: tailorcv.config.models.LlmProvider | None
    :param model: Optional model override.
    :type model: str | None
    :param api_key: Optional API key override.
    :type api_key: str | None
    :param config_path: Optional config path override.
    :type config_path: str | pathlib.Path | None
    :param max_attempts: Max attempts before failing.
    :type max_attempts: int
    :param max_job_chars: Max job description chars to include in prompts.
    :type max_job_chars: int
    """

    provider: LlmProvider | None = None
    model: str | None = None
    api_key: str | None = None
    config_path: str | Path | None = None
    max_attempts: int = 3
    max_job_chars: int = 8000


@dataclass(frozen=True)
class SelectionAttemptError:
    """Single attempt failure detail."""

    attempt: int
    message: str


class SelectionGenerationFailure(RuntimeError):
    """Raised when selection generation cannot produce a valid strict plan."""

    def __init__(self, errors: Sequence[SelectionAttemptError]) -> None:
        self.errors = list(errors)
        details = "; ".join(f"attempt {e.attempt}: {e.message}" for e in self.errors)
        super().__init__(
            f"Selection generation failed after {len(self.errors)} attempts: {details}"
        )


def generate_selection_plan(
    profile: Profile,
    job: Job,
    *,
    options: SelectionGenerationOptions | None = None,
    provider_client: StructuredLlmProvider | None = None,
) -> LlmSelectionPlan:
    """
    Generate an LLM selection plan with strict validation and retry feedback.

    :param profile: Parsed profile input.
    :type profile: tailorcv.schema.profile_schema.Profile
    :param job: Parsed job description.
    :type job: tailorcv.schema.job_schema.Job
    :param options: Optional runtime overrides.
    :type options: SelectionGenerationOptions | None
    :param provider_client: Optional injected provider client for testing.
    :type provider_client: tailorcv.llm.base.StructuredLlmProvider | None
    :return: Strictly valid selection plan.
    :rtype: tailorcv.llm.selection_schema.LlmSelectionPlan
    :raises SelectionGenerationFailure: If all attempts fail.
    """
    resolved_options = options or SelectionGenerationOptions()
    if resolved_options.max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    provider = provider_client or _resolve_provider(resolved_options)
    feedback_errors: list[str] = []
    attempt_errors: list[SelectionAttemptError] = []

    for attempt in range(1, resolved_options.max_attempts + 1):
        invocation = build_selection_invocation(
            profile,
            job,
            feedback_errors=feedback_errors,
            max_job_chars=resolved_options.max_job_chars,
        )

        try:
            plan = provider.generate_structured(
                invocation=invocation,
                schema=LlmSelectionPlan,
            )
            validate_selection_against_profile(profile, plan, strict=True)
            return plan
        except SelectionValidationFailure as exc:
            feedback_errors = [error.message for error in exc.errors]
            message = "Selection validation failed: " + " | ".join(feedback_errors)
            attempt_errors.append(SelectionAttemptError(attempt=attempt, message=message))
        except LlmProviderError as exc:
            message = f"Provider failure: {exc}"
            feedback_errors = [message]
            attempt_errors.append(SelectionAttemptError(attempt=attempt, message=message))

    raise SelectionGenerationFailure(attempt_errors)


def _resolve_provider(options: SelectionGenerationOptions) -> StructuredLlmProvider:
    try:
        resolved = resolve_llm_runtime_config(
            provider=options.provider,
            model=options.model,
            api_key=options.api_key,
            config_path=options.config_path,
        )
    except LlmRuntimeConfigError as exc:
        raise SelectionGenerationFailure(
            [SelectionAttemptError(attempt=0, message=str(exc))]
        ) from exc

    return build_provider(resolved)
