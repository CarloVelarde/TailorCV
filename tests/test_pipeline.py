from __future__ import annotations

from pathlib import Path

from tailorcv.app.pipeline import build_rendercv_document


def test_build_rendercv_document_pipeline(
    profile_valid_path: Path,
    job_min_path: Path,
    selection_valid_path: Path,
) -> None:
    doc = build_rendercv_document(
        profile_path=profile_valid_path,
        job_path=job_min_path,
        selection_path=selection_valid_path,
    )

    assert {"cv", "design", "locale", "settings"} <= set(doc.keys())
    assert "sections" in doc["cv"]
