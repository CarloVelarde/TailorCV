# Schema representing the job description

from pydantic import BaseModel
class Job(BaseModel):
    """
    Representation of a job posting
    """
    raw_text: str
    cleaned_text: str
    keywords: list[str]