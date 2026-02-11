"""OpenAI provider implementation for structured output generation."""

from __future__ import annotations

import json
from typing import Any, Callable

from pydantic import BaseModel

from tailorcv.llm.base import (
    LlmInvocation,
    LlmProviderRequestError,
    LlmProviderResponseError,
)

StructuredModel = type[BaseModel]


class OpenAiProvider:
    """
    OpenAI-backed provider for structured responses.

    This provider intentionally performs lazy client initialization so importing
    the module does not require the `openai` package until execution time.

    :param api_key: OpenAI API key.
    :type api_key: str
    :param model: OpenAI model name.
    :type model: str
    :param client: Optional prebuilt SDK client for testing/injection.
    :type client: typing.Any | None
    :param client_factory: Optional client factory receiving an API key.
    :type client_factory: collections.abc.Callable[[str], typing.Any] | None
    """

    provider_name = "openai"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        client: Any | None = None,
        client_factory: Callable[[str], Any] | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self._client = client
        self._client_factory = client_factory or _build_default_openai_client

    def generate_structured(
        self,
        *,
        invocation: LlmInvocation,
        schema: StructuredModel,
    ) -> BaseModel:
        """
        Generate and validate structured JSON output from OpenAI.

        :param invocation: Prompt payload with system/user prompts.
        :type invocation: tailorcv.llm.base.LlmInvocation
        :param schema: Pydantic schema class to validate.
        :type schema: type[pydantic.BaseModel]
        :return: Parsed and validated schema instance.
        :rtype: pydantic.BaseModel
        :raises LlmProviderRequestError: If OpenAI request fails.
        :raises LlmProviderResponseError: If response JSON/schema is invalid.
        """
        client = self._get_client()
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": invocation.system_prompt},
                    {"role": "user", "content": invocation.user_prompt},
                ],
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            raise LlmProviderRequestError(f"OpenAI request failed: {exc}") from exc

        raw_content = _extract_response_text(response)
        if not raw_content:
            raise LlmProviderResponseError("OpenAI returned an empty response payload.")

        normalized = _strip_json_code_fences(raw_content)
        try:
            payload = json.loads(normalized)
        except Exception as exc:
            raise LlmProviderResponseError(f"OpenAI returned invalid JSON: {exc}") from exc

        try:
            return schema.model_validate(payload)
        except Exception as exc:
            raise LlmProviderResponseError(
                f"OpenAI response failed schema validation for {schema.__name__}: {exc}"
            ) from exc

    def _get_client(self) -> Any:
        if self._client is None:
            self._client = self._client_factory(self.api_key)
        return self._client


def _build_default_openai_client(api_key: str) -> Any:
    try:
        from openai import OpenAI
    except Exception as exc:
        raise LlmProviderRequestError(
            "OpenAI provider requires the `openai` package. Install dependencies and retry."
        ) from exc

    return OpenAI(api_key=api_key)


def _extract_response_text(response: Any) -> str:
    try:
        content = response.choices[0].message.content
    except Exception:
        return ""

    if content is None:
        return ""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
            else:
                text = getattr(item, "text", None)
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts).strip()

    return ""


def _strip_json_code_fences(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```json") and text.endswith("```"):
        return text[7:-3].strip()
    if text.startswith("```") and text.endswith("```"):
        return text[3:-3].strip()
    return text
