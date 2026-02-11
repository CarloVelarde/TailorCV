"""Provider router for LLM integrations."""

from __future__ import annotations

from tailorcv.config.models import LlmProvider
from tailorcv.llm.base import LlmProviderError, StructuredLlmProvider
from tailorcv.llm.providers.openai_provider import OpenAiProvider
from tailorcv.llm.runtime import ResolvedLlmConfig


def build_provider(resolved: ResolvedLlmConfig) -> StructuredLlmProvider:
    """
    Build a concrete provider client from resolved runtime config.

    :param resolved: Effective LLM runtime config.
    :type resolved: tailorcv.llm.runtime.ResolvedLlmConfig
    :return: Provider implementation.
    :rtype: tailorcv.llm.base.StructuredLlmProvider
    :raises LlmProviderError: If provider is unsupported.
    """
    if resolved.provider == LlmProvider.OPENAI:
        return OpenAiProvider(api_key=resolved.api_key, model=resolved.model)

    raise LlmProviderError(f"Unsupported provider: {resolved.provider.value}")
