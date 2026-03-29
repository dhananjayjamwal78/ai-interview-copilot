from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models.job_description import JobDescription
from app.models.resume import Resume
from app.models.user import User
from app.schemas.parsing import (
    JobDescriptionParseResponse,
    ResumeParseResponse,
)
from app.services.parsing_service import parsing_service

router = APIRouter(prefix="/parsing", tags=["Parsing"])


@router.post("/resumes/{resume_id}", response_model=ResumeParseResponse)
def parse_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeParseResponse:
    resume = db.get(Resume, resume_id)
    if resume is None or resume.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Resume not found.")

    try:
        parsed = parsing_service.parse_resume(db, resume)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ResumeParseResponse(id=resume.id, parsed_data=parsed)


@router.post("/job-descriptions/{job_description_id}", response_model=JobDescriptionParseResponse)
def parse_job_description(
    job_description_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobDescriptionParseResponse:
    job_description = db.get(JobDescription, job_description_id)
    if job_description is None or job_description.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job description not found.")

    try:
        parsed = parsing_service.parse_job_description(db, job_description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return JobDescriptionParseResponse(id=job_description.id, parsed_data=parsed)
