from __future__ import annotations

from pathlib import Path

import pytest

from tailorcv.loaders.job_loader import load_job
from tailorcv.loaders.profile_loader import ProfileLoadError, load_profile


def test_load_profile_valid(profile_valid_path: Path) -> None:
    profile = load_profile(profile_valid_path)
    assert profile.meta.name == "Test User"


def test_load_profile_invalid(profile_invalid_path: Path) -> None:
    with pytest.raises(ProfileLoadError) as exc:
        load_profile(profile_invalid_path)
    assert "validation" in str(exc.value).lower()


def test_load_job_keywords_include_lexicon_term(job_min_path: Path) -> None:
    job = load_job(job_min_path)
    assert job.cleaned_text
    assert any(term in job.keywords for term in {"python", "fastapi"})
