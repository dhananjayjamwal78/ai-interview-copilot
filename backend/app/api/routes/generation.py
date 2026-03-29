from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.generation import (
    QuestionGenerationRequest,
    QuestionGenerationResponse,
)
from app.services.question_generation_service import question_generation_service

router = APIRouter(prefix="/generation", tags=["Generation"])


@router.post(
    "/questions",
    response_model=QuestionGenerationResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_questions(
    payload: QuestionGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionGenerationResponse:
    try:
        return question_generation_service.generate_questions(db, current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
