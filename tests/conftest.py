from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture()
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture()
def profile_valid_path(fixtures_dir: Path) -> Path:
    return fixtures_dir / "profile_valid.yaml"


@pytest.fixture()
def profile_invalid_path(fixtures_dir: Path) -> Path:
    return fixtures_dir / "profile_invalid.yaml"


@pytest.fixture()
def profile_empty_path(fixtures_dir: Path) -> Path:
    return fixtures_dir / "profile_empty.yaml"


@pytest.fixture()
def job_min_path(fixtures_dir: Path) -> Path:
    return fixtures_dir / "job_min.txt"


@pytest.fixture()
def selection_valid_path(fixtures_dir: Path) -> Path:
    return fixtures_dir / "selection_valid.json"


@pytest.fixture()
def selection_invalid_id_path(fixtures_dir: Path) -> Path:
    return fixtures_dir / "selection_invalid_id.json"


@pytest.fixture()
def selection_empty_path(fixtures_dir: Path) -> Path:
    return fixtures_dir / "selection_empty.json"
