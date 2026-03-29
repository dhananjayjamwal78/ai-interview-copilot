from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SessionEvaluationView(BaseModel):
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


class SessionAnswerView(BaseModel):
    id: str
    response_text: str
    created_at: datetime
    updated_at: datetime
    evaluations: list[SessionEvaluationView]


class SessionQuestionView(BaseModel):
    id: str
    prompt: str
    category: Optional[str]
    difficulty: Optional[str]
    display_order: int
    answers: list[SessionAnswerView]
