from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from typer.testing import CliRunner

from tailorcv.cli import app
from tailorcv.config.models import LlmProvider
from tailorcv.config.store import load_config

INIT_MODULE = importlib.import_module("tailorcv.cli.init")


def test_cli_init_non_interactive_with_explicit_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.yaml"
    captured: dict[str, str] = {}

    def fake_set_api_key(provider: str, api_key: str) -> None:
        captured[provider] = api_key

    monkeypatch.setattr(INIT_MODULE, "set_api_key", fake_set_api_key)
    monkeypatch.setattr(INIT_MODULE, "get_api_key", lambda provider: None)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "init",
            "--provider",
            "openai",
            "--model",
            "gpt-custom",
            "--api-key",
            "sk-test",
            "--non-interactive",
            "--config-path",
            str(config_path),
        ],
    )

    assert result.exit_code == 0, result.output
    saved = load_config(config_path)
    assert saved.llm.provider == LlmProvider.OPENAI
    assert saved.llm.model == "gpt-custom"
    assert captured["openai"] == "sk-test"


def test_cli_init_non_interactive_requires_api_key_when_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.yaml"

    monkeypatch.setattr(INIT_MODULE, "get_api_key", lambda provider: None)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "init",
            "--provider",
            "openai",
            "--model",
            "gpt-custom",
            "--non-interactive",
            "--config-path",
            str(config_path),
        ],
    )

    assert result.exit_code == 1
    assert "No API key found" in result.output
