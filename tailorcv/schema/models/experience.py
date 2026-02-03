"""Experience entry schema for profile.yaml."""

from typing import List, Optional

from pydantic import BaseModel, Field


class Experience(BaseModel):
    """Experience entry with optional dates and highlights."""

    id: Optional[str] = None
    company: str
    position: str
    location: Optional[str] = None
    date: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    summary: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
