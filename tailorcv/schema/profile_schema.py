from typing import List, Optional

from pydantic import BaseModel, Field

from .models.education import Education
from .models.experience import Experience
from .models.project import Project
from .models.skillentry import SkillEntry


class Social(BaseModel):
    network: str
    username: str


class Meta(BaseModel):
    name: str
    headline: Optional[str] = None
    location: str
    email: str
    phone: Optional[str] = None
    website: Optional[str] = None
    socials: List[Social] = Field(default_factory=list)


class Profile(BaseModel):
    meta: Meta
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    skills: List[SkillEntry] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
