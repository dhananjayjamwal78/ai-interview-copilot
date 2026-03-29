from pydantic import BaseModel


class AnalyticsCategoryPerformance(BaseModel):
    category: str
    questions_attempted: int
    average_score: float
    average_correctness: float
    average_clarity: float
    average_completeness: float


class AnalyticsWeakArea(BaseModel):
    area: str
    metric: str
    average_score: float
    recommendation: str


class AnalyticsSummaryResponse(BaseModel):
    user_id: str
    total_sessions: int
    completed_sessions: int
    questions_generated: int
    questions_attempted: int
    answers_submitted: int
    average_score: float
    average_correctness: float
    average_clarity: float
    average_completeness: float
    average_similarity: float
    category_performance: list[AnalyticsCategoryPerformance]
    weak_areas: list[AnalyticsWeakArea]
