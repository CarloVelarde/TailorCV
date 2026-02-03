"""Education entry schema for profile.yaml."""

from typing import List, Optional

from pydantic import BaseModel, Field


class Education(BaseModel):
    """Education entry with optional dates and highlights."""

    id: Optional[str] = None
    institution: str
    area: str
    degree: Optional[str] = None
    location: Optional[str] = None
    date: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    summary: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
