"""Skill entry schema for profile.yaml."""

from pydantic import BaseModel


class SkillEntry(BaseModel):
    """Labeled skill list entry."""

    label: str
    details: str
