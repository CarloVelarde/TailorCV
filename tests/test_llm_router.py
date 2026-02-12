from __future__ import annotations

from tailorcv.config.models import LlmProvider
from tailorcv.llm.providers.openai_provider import OpenAiProvider
from tailorcv.llm.router import build_provider
from tailorcv.llm.runtime import ResolvedLlmConfig


def test_build_provider_returns_openai_provider() -> None:
    resolved = ResolvedLlmConfig(
        provider=LlmProvider.OPENAI,
        model="gpt-4.1-mini",
        api_key="sk-test",
    )

    provider = build_provider(resolved)
    assert isinstance(provider, OpenAiProvider)
    assert provider.provider_name == "openai"
    assert provider.model == "gpt-4.1-mini"
