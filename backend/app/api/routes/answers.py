from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.evaluation import (
    AnswerSubmissionRequest,
    AnswerSubmissionResponse,
    EvaluationSummary,
)
from app.services.answer_service import answer_service

router = APIRouter(prefix="/answers", tags=["Answers"])


@router.post("", response_model=AnswerSubmissionResponse, status_code=status.HTTP_201_CREATED)
def submit_answer(
    payload: AnswerSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnswerSubmissionResponse:
    try:
        answer, evaluation = answer_service.submit_answer(db, current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return AnswerSubmissionResponse(
        id=answer.id,
        question_id=answer.question_id,
        response_text=answer.response_text,
        created_at=answer.created_at,
        updated_at=answer.updated_at,
        evaluation=EvaluationSummary(
            id=evaluation.id,
            score=float(evaluation.score) if evaluation.score is not None else None,
            correctness_score=float(evaluation.correctness_score)
            if evaluation.correctness_score is not None
            else None,
            clarity_score=float(evaluation.clarity_score)
            if evaluation.clarity_score is not None
            else None,
            completeness_score=float(evaluation.completeness_score)
            if evaluation.completeness_score is not None
            else None,
            semantic_similarity_score=float(evaluation.semantic_similarity_score)
            if evaluation.semantic_similarity_score is not None
            else None,
            rubric_feedback=evaluation.rubric_feedback,
            strengths=evaluation.strengths,
            improvement_areas=evaluation.improvement_areas,
            improvement_suggestions=evaluation.improvement_suggestions,
            model_name=evaluation.model_name,
            created_at=evaluation.created_at,
        ),
    )
