"""Runtime LLM configuration resolution for provider execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tailorcv.config.models import LlmProvider
from tailorcv.config.secrets import (
    SecretStoreError,
    get_api_key,
    get_api_key_env_var,
)
from tailorcv.config.store import ConfigStoreError, load_config


class LlmRuntimeConfigError(ValueError):
    """Raised when effective runtime LLM configuration cannot be resolved."""


@dataclass(frozen=True)
class ResolvedLlmConfig:
    """
    Effective LLM configuration for a generation request.

    :param provider: Selected LLM provider.
    :type provider: tailorcv.config.models.LlmProvider
    :param model: Selected model identifier.
    :type model: str
    :param api_key: API key resolved for provider usage.
    :type api_key: str
    """

    provider: LlmProvider
    model: str
    api_key: str


def resolve_llm_runtime_config(
    *,
    provider: LlmProvider | None = None,
    model: str | None = None,
    api_key: str | None = None,
    config_path: str | Path | None = None,
) -> ResolvedLlmConfig:
    """
    Resolve effective provider/model/API-key values with clear precedence.

    Precedence:
    1) explicit call overrides
    2) persisted config values
    3) environment variable for API key (handled by secret helper)
    4) keychain API key (handled by secret helper)

    :param provider: Optional provider override.
    :type provider: tailorcv.config.models.LlmProvider | None
    :param model: Optional model override.
    :type model: str | None
    :param api_key: Optional explicit API key override.
    :type api_key: str | None
    :param config_path: Optional config path override.
    :type config_path: str | pathlib.Path | None
    :return: Effective resolved config.
    :rtype: ResolvedLlmConfig
    :raises LlmRuntimeConfigError: If effective values cannot be resolved.
    """
    try:
        persisted = load_config(config_path)
    except ConfigStoreError as exc:
        raise LlmRuntimeConfigError(str(exc)) from exc

    resolved_provider = provider if provider is not None else persisted.llm.provider

    resolved_model = model.strip() if model and model.strip() else persisted.llm.model
    if not resolved_model:
        raise LlmRuntimeConfigError("LLM model cannot be empty.")

    resolved_api_key = api_key.strip() if api_key and api_key.strip() else None
    if resolved_api_key is None:
        try:
            resolved_api_key = get_api_key(resolved_provider.value)
        except SecretStoreError as exc:
            raise LlmRuntimeConfigError(str(exc)) from exc

    if not resolved_api_key:
        env_var = get_api_key_env_var(resolved_provider.value)
        raise LlmRuntimeConfigError(
            "No API key available for provider "
            f"'{resolved_provider.value}'. Set {env_var} or run `python -m tailorcv init`."
        )

    return ResolvedLlmConfig(
        provider=resolved_provider,
        model=resolved_model,
        api_key=resolved_api_key,
    )
