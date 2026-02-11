from __future__ import annotations

import pytest

from tailorcv.config.models import LlmConfig, LlmProvider, TailorCvConfig
from tailorcv.llm.runtime import LlmRuntimeConfigError, resolve_llm_runtime_config


def test_resolve_llm_runtime_config_uses_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "tailorcv.llm.runtime.load_config",
        lambda config_path=None: TailorCvConfig(
            llm=LlmConfig(provider=LlmProvider.OPENAI, model="persisted-model")
        ),
    )
    monkeypatch.setattr("tailorcv.llm.runtime.get_api_key", lambda provider: "from-store")

    resolved = resolve_llm_runtime_config(
        provider=LlmProvider.OPENAI,
        model="override-model",
        api_key="override-key",
    )

    assert resolved.provider == LlmProvider.OPENAI
    assert resolved.model == "override-model"
    assert resolved.api_key == "override-key"


def test_resolve_llm_runtime_config_uses_persisted_when_no_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "tailorcv.llm.runtime.load_config",
        lambda config_path=None: TailorCvConfig(
            llm=LlmConfig(provider=LlmProvider.OPENAI, model="persisted-model")
        ),
    )
    monkeypatch.setattr("tailorcv.llm.runtime.get_api_key", lambda provider: "from-store")

    resolved = resolve_llm_runtime_config()

    assert resolved.provider == LlmProvider.OPENAI
    assert resolved.model == "persisted-model"
    assert resolved.api_key == "from-store"


def test_resolve_llm_runtime_config_raises_when_api_key_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "tailorcv.llm.runtime.load_config",
        lambda config_path=None: TailorCvConfig(
            llm=LlmConfig(provider=LlmProvider.OPENAI, model="persisted-model")
        ),
    )
    monkeypatch.setattr("tailorcv.llm.runtime.get_api_key", lambda provider: None)

    with pytest.raises(LlmRuntimeConfigError) as exc:
        resolve_llm_runtime_config()

    assert "OPENAI_API_KEY" in str(exc.value)
