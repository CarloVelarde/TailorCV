"""Filesystem-backed config storage for TailorCV."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

from tailorcv.config.models import TailorCvConfig

CONFIG_PATH_ENV_VAR = "TAILORCV_CONFIG_PATH"
DEFAULT_CONFIG_FILENAME = "config.yaml"


class ConfigStoreError(Exception):
    """Raised when persisted config cannot be read or written."""


def resolve_config_path(config_path: str | Path | None = None) -> Path:
    """
    Resolve the effective config path for TailorCV.

    Precedence:
    1) explicit ``config_path`` argument
    2) ``TAILORCV_CONFIG_PATH`` environment variable
    3) platform default path

    :param config_path: Optional explicit config path.
    :type config_path: str | pathlib.Path | None
    :return: Resolved absolute-ish config file path.
    :rtype: pathlib.Path
    """
    if config_path is not None:
        return Path(config_path).expanduser()

    from_env = os.getenv(CONFIG_PATH_ENV_VAR)
    if from_env:
        return Path(from_env).expanduser()

    if os.name == "nt":
        base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))

    return base / "tailorcv" / DEFAULT_CONFIG_FILENAME


def load_config(config_path: str | Path | None = None) -> TailorCvConfig:
    """
    Load persisted config, returning defaults when the file does not exist.

    :param config_path: Optional explicit config path.
    :type config_path: str | pathlib.Path | None
    :return: Parsed TailorCV config.
    :rtype: tailorcv.config.models.TailorCvConfig
    :raises ConfigStoreError: If persisted config is malformed.
    """
    path = resolve_config_path(config_path)
    if not path.exists():
        return TailorCvConfig()

    try:
        with path.open("r", encoding="utf-8") as file:
            raw = yaml.safe_load(file)
    except Exception as exc:
        raise ConfigStoreError(f"Failed to read config file '{path}': {exc}") from exc

    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ConfigStoreError(f"Config file must contain a mapping at top level: {path}")

    try:
        return TailorCvConfig.model_validate(raw)
    except Exception as exc:
        raise ConfigStoreError(f"Config schema validation failed for '{path}': {exc}") from exc


def save_config(
    config: TailorCvConfig,
    config_path: str | Path | None = None,
) -> Path:
    """
    Persist TailorCV config to disk.

    :param config: Config model to persist.
    :type config: tailorcv.config.models.TailorCvConfig
    :param config_path: Optional explicit config path.
    :type config_path: str | pathlib.Path | None
    :return: Path where config was written.
    :rtype: pathlib.Path
    :raises ConfigStoreError: If writing fails.
    """
    path = resolve_config_path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with path.open("w", encoding="utf-8") as file:
            yaml.safe_dump(config.model_dump(mode="json"), file, sort_keys=False)
    except Exception as exc:
        raise ConfigStoreError(f"Failed to write config file '{path}': {exc}") from exc

    return path
