"""CLI command for first-run TailorCV setup."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from tailorcv.config.models import LlmProvider, TailorCvConfig
from tailorcv.config.secrets import (
    SecretStoreError,
    SecretStoreUnavailableError,
    get_api_key,
    get_api_key_env_var,
    set_api_key,
)
from tailorcv.config.store import ConfigStoreError, load_config, resolve_config_path, save_config


def init(
    provider: LlmProvider | None = typer.Option(
        None,
        help="LLM provider to use (currently: openai).",
    ),
    model: str | None = typer.Option(
        None,
        help="Default model name to use for LLM calls.",
    ),
    api_key: str | None = typer.Option(
        None,
        help="API key for the selected provider. If omitted, the command may prompt.",
    ),
    non_interactive: bool = typer.Option(
        False,
        help="Disable prompts and require explicit inputs/environment configuration.",
    ),
    force: bool = typer.Option(
        False,
        help="Prompt for values even when existing config/key values are already available.",
    ),
    config_path: Path | None = typer.Option(
        None,
        help="Optional config path override.",
    ),
) -> None:
    """
    Initialize persistent TailorCV LLM configuration.

    :param provider: LLM provider identifier.
    :type provider: tailorcv.config.models.LlmProvider | None
    :param model: LLM model name.
    :type model: str | None
    :param api_key: Provider API key.
    :type api_key: str | None
    :param non_interactive: Whether to disable prompts.
    :type non_interactive: bool
    :param force: Whether to re-prompt despite existing values.
    :type force: bool
    :param config_path: Optional config path override.
    :type config_path: pathlib.Path | None
    :return: None.
    :rtype: None
    """
    interactive = _is_interactive() and not non_interactive
    resolved_config_path = resolve_config_path(config_path)
    config_exists = resolved_config_path.exists()

    try:
        config = load_config(config_path)
    except ConfigStoreError as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    selected_provider = _resolve_provider(provider, config, interactive, force, config_exists)
    selected_model = _resolve_model(model, config, interactive, force, config_exists)

    config.llm.provider = selected_provider
    config.llm.model = selected_model

    try:
        _resolve_and_store_api_key(
            provider=selected_provider,
            explicit_api_key=api_key,
            interactive=interactive,
            force=force,
        )
    except (SecretStoreError, ValueError) as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    try:
        written_config_path = save_config(config, config_path)
    except ConfigStoreError as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    typer.secho(f"Config saved: {written_config_path}", fg=typer.colors.GREEN)
    typer.secho(
        f"Default provider/model: {selected_provider.value}/{selected_model}",
        fg=typer.colors.GREEN,
    )


def _resolve_provider(
    provider: LlmProvider | None,
    config: TailorCvConfig,
    interactive: bool,
    force: bool,
    config_exists: bool,
) -> LlmProvider:
    if provider is not None:
        return provider
    if not interactive or (config_exists and not force):
        return config.llm.provider

    raw = typer.prompt("Provider", default=config.llm.provider.value).strip().lower()
    try:
        return LlmProvider(raw)
    except ValueError as exc:
        raise ValueError(f"Unsupported provider '{raw}'.") from exc


def _resolve_model(
    model: str | None,
    config: TailorCvConfig,
    interactive: bool,
    force: bool,
    config_exists: bool,
) -> str:
    if model is not None and model.strip():
        return model.strip()
    if not interactive or (config_exists and not force):
        return config.llm.model

    prompted = typer.prompt("Model", default=config.llm.model).strip()
    if not prompted:
        raise ValueError("Model cannot be empty.")
    return prompted


def _resolve_and_store_api_key(
    *,
    provider: LlmProvider,
    explicit_api_key: str | None,
    interactive: bool,
    force: bool,
) -> None:
    provider_value = provider.value
    env_var = get_api_key_env_var(provider_value)

    if explicit_api_key and explicit_api_key.strip():
        set_api_key(provider_value, explicit_api_key.strip())
        return

    try:
        existing_key = get_api_key(provider_value)
    except SecretStoreUnavailableError as exc:
        if not interactive:
            raise ValueError(
                f"{exc} Set {env_var} in your environment for non-interactive usage."
            ) from exc
        existing_key = None

    needs_key = force or not existing_key
    if not needs_key:
        return

    if not interactive:
        raise ValueError(
            f"No API key found for provider '{provider_value}'. Pass --api-key or set {env_var}."
        )

    prompted = typer.prompt("API key", hide_input=True).strip()
    if not prompted:
        raise ValueError("API key cannot be empty.")
    set_api_key(provider_value, prompted)


def _is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()
