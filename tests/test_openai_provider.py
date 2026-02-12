from __future__ import annotations

import pytest

from tailorcv.llm.base import LlmInvocation, LlmProviderResponseError
from tailorcv.llm.providers.openai_provider import OpenAiProvider
from tailorcv.llm.selection_schema import LlmSelectionPlan


class _FakeMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class _FakeChoice:
    def __init__(self, content: str) -> None:
        self.message = _FakeMessage(content)


class _FakeResponse:
    def __init__(self, content: str) -> None:
        self.choices = [_FakeChoice(content)]


class _FakeChatCompletions:
    def __init__(self, content: str) -> None:
        self._content = content

    def create(self, **kwargs: object) -> _FakeResponse:
        return _FakeResponse(self._content)


class _FakeChat:
    def __init__(self, content: str) -> None:
        self.completions = _FakeChatCompletions(content)


class _FakeClient:
    def __init__(self, content: str) -> None:
        self.chat = _FakeChat(content)


def test_openai_provider_parses_structured_json() -> None:
    provider = OpenAiProvider(
        api_key="sk-test",
        model="gpt-4.1-mini",
        client=_FakeClient(
            '{"selected_experience_ids":["exp1"],"selected_skill_labels":["Languages"]}'
        ),
    )

    result = provider.generate_structured(
        invocation=LlmInvocation(
            system_prompt="system",
            user_prompt="user",
        ),
        schema=LlmSelectionPlan,
    )

    assert result.selected_experience_ids == ["exp1"]
    assert result.selected_skill_labels == ["Languages"]


def test_openai_provider_rejects_invalid_json() -> None:
    provider = OpenAiProvider(
        api_key="sk-test",
        model="gpt-4.1-mini",
        client=_FakeClient("{this-is-not-json}"),
    )

    with pytest.raises(LlmProviderResponseError) as exc:
        provider.generate_structured(
            invocation=LlmInvocation(system_prompt="system", user_prompt="user"),
            schema=LlmSelectionPlan,
        )

    assert "invalid JSON" in str(exc.value)


def test_openai_provider_rejects_schema_mismatch() -> None:
    provider = OpenAiProvider(
        api_key="sk-test",
        model="gpt-4.1-mini",
        client=_FakeClient('{"selected_experience_ids":"not-a-list"}'),
    )

    with pytest.raises(LlmProviderResponseError) as exc:
        provider.generate_structured(
            invocation=LlmInvocation(system_prompt="system", user_prompt="user"),
            schema=LlmSelectionPlan,
        )

    assert "schema validation" in str(exc.value)
