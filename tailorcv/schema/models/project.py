from typing import List, Optional

from pydantic import BaseModel


class Project(BaseModel):
    id: str
    name: str
    summary: Optional[str] = None
    highlights: List[str]
    tags: List[str] = []
