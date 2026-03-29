from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AnswerSubmissionRequest(BaseModel):
    question_id: str
    response_text: str = Field(min_length=1)

    @field_validator("response_text")
    @classmethod
    def validate_response_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Answer text cannot be empty.")
        return cleaned


class EvaluationSummary(BaseModel):
    id: str
    score: Optional[float]
    correctness_score: Optional[float]
    clarity_score: Optional[float]
    completeness_score: Optional[float]
    semantic_similarity_score: Optional[float]
    rubric_feedback: Optional[str]
    strengths: Optional[str]
    improvement_areas: Optional[str]
    improvement_suggestions: Optional[str]
    model_name: Optional[str]
    created_at: datetime


class AnswerSubmissionResponse(BaseModel):
    id: str
    question_id: str
    response_text: str
    created_at: datetime
    updated_at: datetime
    evaluation: EvaluationSummary
