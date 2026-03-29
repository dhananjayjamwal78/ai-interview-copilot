from typing import Optional

from pydantic import BaseModel


class ResumeParsedData(BaseModel):
    skills: list[str]
    roles: list[str]
    domains: list[str]
    experience_years: Optional[float]
    metadata: dict


class JobDescriptionParsedData(BaseModel):
    required_skills: list[str]
    preferred_skills: list[str]
    requirements: list[str]
    role: Optional[str]
    domain: Optional[str]
    experience_years: Optional[float]
    metadata: dict


class ResumeParseResponse(BaseModel):
    id: str
    parsed_data: ResumeParsedData


class JobDescriptionParseResponse(BaseModel):
    id: str
    parsed_data: JobDescriptionParsedData
