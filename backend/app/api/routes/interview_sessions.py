from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.session import (
    InterviewSessionCreateRequest,
    InterviewSessionDetail,
    InterviewSessionSummary,
)
from app.services.interview_session_service import interview_session_service

router = APIRouter(prefix="/sessions", tags=["Interview Sessions"])


@router.post("", response_model=InterviewSessionDetail, status_code=status.HTTP_201_CREATED)
def create_interview_session(
    payload: InterviewSessionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewSessionDetail:
    try:
        return interview_session_service.create_session(db, current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[InterviewSessionSummary])
def list_interview_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[InterviewSessionSummary]:
    return interview_session_service.list_sessions(db, user_id=current_user.id)


@router.get("/{session_id}", response_model=InterviewSessionDetail)
def get_interview_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterviewSessionDetail:
    session = interview_session_service.get_session(db, current_user.id, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    return session
