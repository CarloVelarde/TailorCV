"""Base interfaces and exceptions for LLM provider integrations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

StructuredModel = TypeVar("StructuredModel", bound=BaseModel)


class LlmProviderError(RuntimeError):
    """Base error for provider integration failures."""


class LlmProviderRequestError(LlmProviderError):
    """Raised when a provider request cannot be sent."""


class LlmProviderResponseError(LlmProviderError):
    """Raised when a provider response is invalid for the expected schema."""


@dataclass(frozen=True)
class LlmInvocation:
    """
    Prompt payload sent to a provider.

    :param system_prompt: System instruction prompt.
    :type system_prompt: str
    :param user_prompt: User prompt payload.
    :type user_prompt: str
    """

    system_prompt: str
    user_prompt: str


@runtime_checkable
class StructuredLlmProvider(Protocol):
    """Protocol for providers that return structured Pydantic output."""

    provider_name: str
    model: str

    def generate_structured(
        self,
        *,
        invocation: LlmInvocation,
        schema: type[StructuredModel],
    ) -> StructuredModel:
        """
        Generate structured output constrained to a Pydantic schema.

        :param invocation: Prompt invocation payload.
        :type invocation: LlmInvocation
        :param schema: Pydantic schema class to validate against.
        :type schema: type[StructuredModel]
        :return: Validated model instance.
        :rtype: StructuredModel
        """
