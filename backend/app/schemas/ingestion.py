from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.parsing import JobDescriptionParsedData, ResumeParsedData


class ResumeTextCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    original_filename: str = Field(default="resume.txt", min_length=1, max_length=255)
    resume_text: str = Field(min_length=1)

    @field_validator("title", "original_filename", "resume_text")
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty.")
        return cleaned


class JobDescriptionCreate(BaseModel):
    role_title: str = Field(min_length=1, max_length=255)
    company_name: Optional[str] = Field(default=None, max_length=255)
    source_url: Optional[str] = Field(default=None, max_length=1024)
    raw_text: str = Field(min_length=1)

    @field_validator("role_title", "raw_text")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty.")
        return cleaned

    @field_validator("company_name", "source_url")
    @classmethod
    def normalize_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class ResumeIngestionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    original_filename: str
    file_path: Optional[str]
    extracted_text: str
    extracted_text_preview: str
    extracted_text_length: int
    parsed_data: ResumeParsedData


class JobDescriptionIngestionResponse(BaseModel):
    id: str
    user_id: str
    role_title: str
    company_name: Optional[str]
    source_url: Optional[str]
    raw_text: str
    raw_text_preview: str
    raw_text_length: int
    parsed_data: JobDescriptionParsedData
