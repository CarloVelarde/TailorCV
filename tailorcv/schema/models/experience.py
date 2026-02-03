from typing import List

from pydantic import BaseModel


class Experience(BaseModel):
    id: str
    company: str
    position: str
    location: str
    start_date: str
    end_date: str
    highlights: List[str]
    tags: List[str] = []
