from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, model_validator

# --------------------------------------------------------------------
# TailorCV "thin" RenderCV schema
#
# Purpose:
# - Provide a structured internal target for generating RenderCV-compatible YAML.
# - Keep it permissive where RenderCV is permissive (entries allow extra keys).
# - Enforce a few high-value constraints early (e.g., one entry type per section).
#
# Note:
# - Final/authoritative validation should still be done using RenderCV's own models.
# --------------------------------------------------------------------

StrOrListStr = Union[str, List[str]]


# -------------------------
# Header helpers
# -------------------------


class SocialNetwork(BaseModel):
    """RenderCV: cv.social_networks item."""

    model_config = ConfigDict(extra="forbid")

    network: str
    username: str


class CustomConnection(BaseModel):
    """RenderCV: cv.custom_connections item."""

    model_config = ConfigDict(extra="forbid")

    placeholder: str
    url: Optional[str] = None
    fontawesome_icon: Optional[str] = None


# -------------------------
# Entry base / shared fields
# -------------------------


class EntryBase(BaseModel):
    """
    Base for entries placed under cv.sections.<section_title>.

    RenderCV allows arbitrary keys in entries (templates can reference them),
    so we allow extra fields here.
    """

    model_config = ConfigDict(extra="allow")


class EntryWithDates(EntryBase):
    """Common date fields used by many RenderCV entry types."""

    date: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None  # "present" is commonly used


class EntryWithSummaryHighlights(EntryWithDates):
    """Common optional fields used by many RenderCV entry types."""

    location: Optional[str] = None
    summary: Optional[str] = None
    highlights: Optional[List[str]] = None


# -------------------------
# RenderCV entry types
# -------------------------


class EducationEntry(EntryWithSummaryHighlights):
    """RenderCV EducationEntry."""

    institution: str
    area: str
    degree: Optional[str] = None


class ExperienceEntry(EntryWithSummaryHighlights):
    """RenderCV ExperienceEntry."""

    company: str
    position: str


class NormalEntry(EntryWithSummaryHighlights):
    """RenderCV NormalEntry."""

    name: str


class PublicationEntry(EntryBase):
    """RenderCV PublicationEntry."""

    title: str
    authors: List[str]

    summary: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    journal: Optional[str] = None
    date: Optional[str] = None


class OneLineEntry(EntryBase):
    """RenderCV OneLineEntry."""

    label: str
    details: str


class BulletEntry(EntryBase):
    """RenderCV BulletEntry."""

    bullet: str


class NumberedEntry(EntryBase):
    """RenderCV NumberedEntry."""

    number: str


class ReversedNumberedEntry(EntryBase):
    """RenderCV ReversedNumberedEntry."""

    reversed_number: str


TextEntry = str  # RenderCV: a plain string is a TextEntry

Entry = Union[
    TextEntry,
    EducationEntry,
    ExperienceEntry,
    NormalEntry,
    PublicationEntry,
    OneLineEntry,
    BulletEntry,
    NumberedEntry,
    ReversedNumberedEntry,
]


# -------------------------
# Sections validation
# -------------------------


def _classify_entry(e: Entry) -> str:
    """Return a stable entry-type label for enforcing per-section type uniformity."""
    if isinstance(e, str):
        return "TextEntry"
    if isinstance(e, EducationEntry):
        return "EducationEntry"
    if isinstance(e, ExperienceEntry):
        return "ExperienceEntry"
    if isinstance(e, PublicationEntry):
        return "PublicationEntry"
    if isinstance(e, OneLineEntry):
        return "OneLineEntry"
    if isinstance(e, BulletEntry):
        return "BulletEntry"
    if isinstance(e, NumberedEntry):
        return "NumberedEntry"
    if isinstance(e, ReversedNumberedEntry):
        return "ReversedNumberedEntry"
    if isinstance(e, NormalEntry):
        return "NormalEntry"
    return "Unknown"


def _enforce_one_type_per_section(
    sections: Dict[str, List[Entry]],
) -> Dict[str, List[Entry]]:
    """RenderCV rule: each section must contain only one entry type."""
    for title, entries in sections.items():
        if not entries:
            continue
        first_type = _classify_entry(entries[0])
        for idx, e in enumerate(entries[1:], start=1):
            t = _classify_entry(e)
            if t != first_type:
                raise ValueError(
                    f"Section '{title}' mixes entry types: first is {first_type}, "
                    f"but entry #{idx + 1} is {t}."
                )
    return sections


# -------------------------
# CV model
# -------------------------


class Cv(BaseModel):
    """RenderCV `cv` block: header fields + sections."""

    model_config = ConfigDict(extra="forbid")

    # Header
    name: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    email: Optional[StrOrListStr] = None
    photo: Optional[str] = None
    phone: Optional[StrOrListStr] = None
    website: Optional[StrOrListStr] = None

    social_networks: Optional[List[SocialNetwork]] = None
    custom_connections: Optional[List[CustomConnection]] = None

    # Content
    sections: Dict[str, List[Entry]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_sections(self) -> "Cv":
        self.sections = _enforce_one_type_per_section(self.sections)
        return self


# -------------------------
# Full document wrapper
# -------------------------


class RenderCvDocument(BaseModel):
    """
    Thin top-level wrapper for a RenderCV YAML file.
    TailorCV mainly generates `cv`; other blocks are user-controlled.
    """

    model_config = ConfigDict(extra="allow")

    cv: Cv
    design: Optional[Dict[str, Any]] = None
    locale: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
