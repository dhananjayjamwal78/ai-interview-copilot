from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.generation import QuestionCategory
from app.schemas.session_view import SessionQuestionView


class InterviewSessionCreateRequest(BaseModel):
    resume_id: Optional[str] = None
    job_description_id: Optional[str] = None
    title: Optional[str] = Field(default=None, max_length=255)
    target_role: Optional[str] = Field(default=None, max_length=255)
    target_skills: list[str] = Field(default_factory=list)
    question_categories: list[QuestionCategory] = Field(default_factory=list)
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_source(self):
        if (
            not self.resume_id
            and not self.job_description_id
            and not self.title
            and not self.target_role
        ):
            raise ValueError(
                "Provide at least a resume, job description, title, or target role."
            )
        return self


class InterviewSessionSummary(BaseModel):
    id: str
    user_id: str
    resume_id: Optional[str]
    job_description_id: Optional[str]
    title: str
    target_role: Optional[str]
    target_skills: list[str]
    question_categories: list[str]
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    question_count: int


class InterviewSessionDetail(InterviewSessionSummary):
    notes: Optional[str]
    questions: list[SessionQuestionView]
