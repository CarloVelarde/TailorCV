from typing import List

from pydantic import BaseModel


class BaseItem(BaseModel):
    id: str
    tags: List[str] = []
