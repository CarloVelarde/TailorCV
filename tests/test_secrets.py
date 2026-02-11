from __future__ import annotations

from types import SimpleNamespace

import pytest

from tailorcv.config import secrets


def test_get_api_key_prefers_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "from-env")
    monkeypatch.setattr(secrets, "get_stored_api_key", lambda provider: "from-store")

    assert secrets.get_api_key("openai") == "from-env"


def test_set_and_get_stored_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    store: dict[tuple[str, str], str] = {}

    def fake_set_password(service: str, account: str, value: str) -> None:
        store[(service, account)] = value

    def fake_get_password(service: str, account: str) -> str | None:
        return store.get((service, account))

    fake_keyring = SimpleNamespace(
        set_password=fake_set_password,
        get_password=fake_get_password,
    )

    monkeypatch.setattr(secrets, "_require_keyring", lambda: None)
    monkeypatch.setattr(secrets, "keyring", fake_keyring)

    secrets.set_api_key("openai", "stored-key")
    assert secrets.get_stored_api_key("openai") == "stored-key"
