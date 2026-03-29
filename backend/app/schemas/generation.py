from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


QuestionCategory = Literal["technical", "project-based", "behavioral", "hr/general"]
QuestionDifficulty = Literal["easy", "medium", "hard"]


class GeneratedQuestionItem(BaseModel):
    prompt: str = Field(min_length=1)
    category: QuestionCategory
    difficulty: QuestionDifficulty
    suggested_answer: str = Field(min_length=1)
    answer_example: str = Field(min_length=1)


class QuestionGenerationRequest(BaseModel):
    resume_id: Optional[str] = None
    job_description_id: Optional[str] = None
    interview_session_id: Optional[str] = None
    categories: list[QuestionCategory] = Field(
        default_factory=lambda: ["technical", "project-based", "behavioral", "hr/general"]
    )
    difficulty: QuestionDifficulty = "medium"
    question_count: int = Field(default=8, ge=1, le=20)
    session_title: Optional[str] = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_sources(self):
        if not self.resume_id and not self.job_description_id and not self.interview_session_id:
            raise ValueError(
                "At least one of resume_id, job_description_id, or interview_session_id is required."
            )
        return self


class QuestionGenerationResponse(BaseModel):
    interview_session_id: str
    source_mode: Literal["resume_only", "jd_only", "resume_and_jd", "existing_session"]
    generated_count: int
    questions: list[GeneratedQuestionItem]
    provider: str
    model: str
