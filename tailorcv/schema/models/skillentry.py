from pydantic import BaseModel


class SkillEntry(BaseModel):
    label: str
    details: str
