from typing import List, Optional

from pydantic import BaseModel, Field


class BaseItem(BaseModel):
    id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
