from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import decode_access_token
from app.db import get_db
from app.models.user import User
from app.schemas.ingestion import (
    JobDescriptionCreate,
    JobDescriptionIngestionResponse,
    ResumeIngestionResponse,
    ResumeTextCreate,
)
from app.schemas.parsing import JobDescriptionParsedData, ResumeParsedData
from app.services.ingestion_service import ingestion_service

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])


def _resume_response(payload) -> ResumeIngestionResponse:
    extracted_text = payload.extracted_text or ""
    return ResumeIngestionResponse(
        id=payload.id,
        user_id=payload.user_id,
        title=payload.title,
        original_filename=payload.original_filename,
        file_path=payload.file_path,
        extracted_text=extracted_text,
        extracted_text_preview=extracted_text[:280],
        extracted_text_length=len(extracted_text),
        parsed_data=ResumeParsedData(
            skills=payload.parsed_skills,
            roles=payload.parsed_roles,
            domains=payload.parsed_domains,
            experience_years=payload.parsed_experience_years,
            metadata=payload.parsed_metadata,
        ),
    )


@router.post(
    "/resumes/text",
    response_model=ResumeIngestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_resume_text(
    payload: ResumeTextCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeIngestionResponse:
    try:
        resume = ingestion_service.create_resume_from_text(db, current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _resume_response(resume)


@router.post(
    "/resumes/upload",
    response_model=ResumeIngestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_resume_upload(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeIngestionResponse:
    if not title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title is required.",
        )
    try:
        resume = ingestion_service.create_resume_from_upload(
            db,
            current_user=current_user,
            title=title.strip(),
            file=file,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _resume_response(resume)


@router.get("/resumes/{resume_id}", response_model=ResumeIngestionResponse)
def get_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeIngestionResponse:
    resume = ingestion_service.get_resume(db, current_user, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return _resume_response(resume)


@router.get("/resumes/{resume_id}/file")
def download_resume_file(
    resume_id: str,
    preview_token: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    token = preview_token
    if not token and authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        user_id = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    current_user = db.get(User, user_id)
    if current_user is None:
        raise HTTPException(status_code=401, detail="User not found.")

    resume = ingestion_service.get_resume(db, current_user, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found.")
    if not resume.file_path:
        raise HTTPException(status_code=404, detail="No uploaded file is available for this resume.")
    media_type = "application/pdf" if resume.original_filename.lower().endswith(".pdf") else "application/octet-stream"
    return FileResponse(
        path=resume.file_path,
        filename=resume.original_filename,
        media_type=media_type,
        content_disposition_type="inline" if media_type == "application/pdf" else "attachment",
    )


@router.post(
    "/job-descriptions",
    response_model=JobDescriptionIngestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_job_description(
    payload: JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobDescriptionIngestionResponse:
    try:
        job_description = ingestion_service.create_job_description(
            db, current_user, payload
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return JobDescriptionIngestionResponse(
        id=job_description.id,
        user_id=job_description.user_id,
        role_title=job_description.role_title,
        company_name=job_description.company_name,
        source_url=job_description.source_url,
        raw_text=job_description.raw_text,
        raw_text_preview=job_description.raw_text[:280],
        raw_text_length=len(job_description.raw_text),
        parsed_data=JobDescriptionParsedData(
            required_skills=job_description.required_skills,
            preferred_skills=job_description.preferred_skills,
            requirements=job_description.extracted_requirements,
            role=job_description.parsed_role,
            domain=job_description.parsed_domain,
            experience_years=job_description.parsed_experience_years,
            metadata=job_description.parsed_metadata,
        ),
    )


@router.get("/job-descriptions/{job_description_id}", response_model=JobDescriptionIngestionResponse)
def get_job_description(
    job_description_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobDescriptionIngestionResponse:
    job_description = ingestion_service.get_job_description(
        db,
        current_user,
        job_description_id,
    )
    if job_description is None:
        raise HTTPException(status_code=404, detail="Job description not found.")
    return JobDescriptionIngestionResponse(
        id=job_description.id,
        user_id=job_description.user_id,
        role_title=job_description.role_title,
        company_name=job_description.company_name,
        source_url=job_description.source_url,
        raw_text=job_description.raw_text,
        raw_text_preview=job_description.raw_text[:280],
        raw_text_length=len(job_description.raw_text),
        parsed_data=JobDescriptionParsedData(
            required_skills=job_description.required_skills,
            preferred_skills=job_description.preferred_skills,
            requirements=job_description.extracted_requirements,
            role=job_description.parsed_role,
            domain=job_description.parsed_domain,
            experience_years=job_description.parsed_experience_years,
            metadata=job_description.parsed_metadata,
        ),
    )
