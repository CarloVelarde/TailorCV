"""Common base fields used by profile entries."""

from typing import List, Optional

from pydantic import BaseModel, Field


class BaseItem(BaseModel):
    """Common fields for profile entries that support tags."""

    id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
