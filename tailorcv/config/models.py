"""Pydantic models for persisted TailorCV configuration."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"


class LlmProvider(StrEnum):
    """Supported LLM providers."""

    OPENAI = "openai"


class LlmConfig(BaseModel):
    """Persisted LLM defaults used by the CLI."""

    provider: LlmProvider = LlmProvider.OPENAI
    model: str = DEFAULT_OPENAI_MODEL


class TailorCvConfig(BaseModel):
    """Top-level persisted TailorCV config."""

    llm: LlmConfig = Field(default_factory=LlmConfig)
