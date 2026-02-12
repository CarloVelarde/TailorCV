"""Secret management helpers for provider API keys."""

from __future__ import annotations

import os

try:  # pragma: no cover - import guard
    import keyring
    from keyring.errors import KeyringError, NoKeyringError, PasswordDeleteError
except Exception:  # pragma: no cover - handled via explicit checks
    keyring = None

    class KeyringError(Exception):
        """Fallback keyring error when keyring is unavailable."""

    class NoKeyringError(KeyringError):
        """Fallback no-backend keyring error."""

    class PasswordDeleteError(KeyringError):
        """Fallback password delete error."""


KEYRING_SERVICE_NAME = "tailorcv"


class SecretStoreError(Exception):
    """Raised when interaction with secret storage fails."""


class SecretStoreUnavailableError(SecretStoreError):
    """Raised when secure key storage is unavailable on this system."""


def get_api_key_env_var(provider: str) -> str:
    """
    Return the environment variable name for a provider API key.

    :param provider: Provider identifier (e.g., ``openai``).
    :type provider: str
    :return: Environment variable name.
    :rtype: str
    """
    normalized = provider.strip().lower()
    if normalized == "openai":
        return "OPENAI_API_KEY"
    return f"{normalized.upper()}_API_KEY"


def get_api_key(provider: str) -> str | None:
    """
    Resolve an API key for a provider.

    Precedence:
    1) environment variable override
    2) OS keychain via keyring

    :param provider: Provider identifier.
    :type provider: str
    :return: API key or None if unavailable.
    :rtype: str | None
    :raises SecretStoreError: If keyring access fails unexpectedly.
    """
    env_var = get_api_key_env_var(provider)
    from_env = os.getenv(env_var)
    if from_env and from_env.strip():
        return from_env.strip()

    return get_stored_api_key(provider)


def get_stored_api_key(provider: str) -> str | None:
    """
    Read an API key from OS keychain storage.

    :param provider: Provider identifier.
    :type provider: str
    :return: Stored API key or None.
    :rtype: str | None
    :raises SecretStoreError: If keyring access fails unexpectedly.
    """
    _require_keyring()
    try:
        return keyring.get_password(KEYRING_SERVICE_NAME, _account_name(provider))
    except NoKeyringError as exc:
        raise SecretStoreUnavailableError(
            "No OS keyring backend is available. Set OPENAI_API_KEY (or provider "
            "equivalent) in your environment for now."
        ) from exc
    except KeyringError as exc:
        raise SecretStoreError(f"Failed to read API key from keyring: {exc}") from exc


def set_api_key(provider: str, api_key: str) -> None:
    """
    Store an API key in OS keychain storage.

    :param provider: Provider identifier.
    :type provider: str
    :param api_key: API key to store.
    :type api_key: str
    :return: None
    :rtype: None
    :raises SecretStoreError: If keyring access fails.
    """
    _require_keyring()
    try:
        keyring.set_password(KEYRING_SERVICE_NAME, _account_name(provider), api_key)
    except NoKeyringError as exc:
        raise SecretStoreUnavailableError(
            "No OS keyring backend is available. Use environment variables for API keys."
        ) from exc
    except KeyringError as exc:
        raise SecretStoreError(f"Failed to store API key in keyring: {exc}") from exc


def delete_api_key(provider: str) -> None:
    """
    Delete a provider API key from keychain storage if present.

    :param provider: Provider identifier.
    :type provider: str
    :return: None
    :rtype: None
    :raises SecretStoreError: If keyring access fails.
    """
    _require_keyring()
    try:
        keyring.delete_password(KEYRING_SERVICE_NAME, _account_name(provider))
    except NoKeyringError as exc:
        raise SecretStoreUnavailableError(
            "No OS keyring backend is available. Nothing to delete from secure storage."
        ) from exc
    except PasswordDeleteError:
        return
    except KeyringError as exc:
        raise SecretStoreError(f"Failed to delete API key from keyring: {exc}") from exc


def _account_name(provider: str) -> str:
    return f"{provider.strip().lower()}_api_key"


def _require_keyring() -> None:
    if keyring is None:
        raise SecretStoreUnavailableError(
            "The 'keyring' package is not available. Install dependencies or use environment "
            "variables for API keys."
        )
