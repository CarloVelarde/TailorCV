from typing import List

from pydantic import BaseModel


class Education(BaseModel):
    id: str
    institution: str
    area: str
    degree: str
    location: str
    start_date: str
    end_date: str
    highlights: List[str] = []
    tags: List[str] = []
