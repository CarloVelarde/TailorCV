"""Project entry schema for profile.yaml."""

from typing import List, Optional

from pydantic import BaseModel, Field


class Project(BaseModel):
    """Project entry with optional dates and highlights."""

    id: Optional[str] = None
    name: str
    summary: Optional[str] = None
    location: Optional[str] = None
    date: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
