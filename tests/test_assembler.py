from __future__ import annotations

from tailorcv.assemblers.rendercv_document import assemble_rendercv_document


def test_assembler_defaults_inserted() -> None:
    cv_doc = {"cv": {"name": "Test User"}}
    doc = assemble_rendercv_document(cv_doc)
    assert {"cv", "design", "locale", "settings"} <= set(doc.keys())
    assert doc["design"]
    assert doc["locale"]


def test_assembler_overrides_take_precedence() -> None:
    cv_doc = {"cv": {"name": "Test User"}}
    design = {"theme": "classic"}
    locale = {"language": "english"}
    settings = {"current_date": "2024-01-01"}
    doc = assemble_rendercv_document(
        cv_doc,
        design=design,
        locale=locale,
        settings=settings,
    )
    assert doc["design"] == design
    assert doc["locale"] == locale
    assert doc["settings"] == settings
