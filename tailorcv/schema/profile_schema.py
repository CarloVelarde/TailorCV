from typing import List, Optional

from pydantic import BaseModel

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
    socials: List[Social] = []


class Profile(BaseModel):
    meta: Meta
    education: List[Education] = []
    experience: List[Experience] = []
    projects: List[Project] = []
    skills: List[SkillEntry] = []
    certifications: List[str] = []
    interests: List[str] = []
