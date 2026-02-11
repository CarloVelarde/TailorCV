from __future__ import annotations

from pathlib import Path

import pytest

from tailorcv.config.models import DEFAULT_OPENAI_MODEL, LlmConfig, LlmProvider, TailorCvConfig
from tailorcv.config.store import load_config, resolve_config_path, save_config


def test_load_config_returns_defaults_when_missing(tmp_path: Path) -> None:
    config_path = tmp_path / "missing.yaml"
    config = load_config(config_path)

    assert config.llm.provider == LlmProvider.OPENAI
    assert config.llm.model == DEFAULT_OPENAI_MODEL


def test_save_and_load_config_roundtrip(tmp_path: Path) -> None:
    config_path = tmp_path / "tailorcv.yaml"
    expected = TailorCvConfig(
        llm=LlmConfig(
            provider=LlmProvider.OPENAI,
            model="gpt-test-model",
        )
    )

    saved_path = save_config(expected, config_path)
    loaded = load_config(config_path)

    assert saved_path == config_path
    assert loaded == expected


def test_resolve_config_path_prefers_env_var(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    env_path = tmp_path / "env-config.yaml"
    monkeypatch.setenv("TAILORCV_CONFIG_PATH", str(env_path))

    resolved = resolve_config_path()
    assert resolved == env_path
