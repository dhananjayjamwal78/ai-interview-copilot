from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.job_description import JobDescription
from app.models.resume import Resume
from app.models.user import User
from app.schemas.ingestion import JobDescriptionCreate, ResumeTextCreate
from app.services.parsing_service import parsing_service
from app.utils.file_handler import (
    build_storage_path,
    validate_file_size,
    validate_upload_file,
)
from app.utils.text_extraction import extract_text_from_file, validate_extracted_text


class IngestionService:
    def get_resume(self, db: Session, current_user: User, resume_id: str) -> Resume | None:
        resume = db.get(Resume, resume_id)
        if resume is None or resume.user_id != current_user.id:
            return None
        return resume

    def get_job_description(
        self,
        db: Session,
        current_user: User,
        job_description_id: str,
    ) -> JobDescription | None:
        job_description = db.get(JobDescription, job_description_id)
        if job_description is None or job_description.user_id != current_user.id:
            return None
        return job_description

    def create_resume_from_text(
        self,
        db: Session,
        current_user: User,
        payload: ResumeTextCreate,
    ) -> Resume:
        extracted_text = validate_extracted_text(payload.resume_text)
        title = payload.title.strip()
        original_filename = payload.original_filename.strip()

        resume = Resume(
            user_id=current_user.id,
            title=title,
            original_filename=original_filename,
            extracted_text=extracted_text,
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        parsing_service.parse_resume(db, resume)
        db.refresh(resume)
        return resume

    def create_resume_from_upload(
        self,
        db: Session,
        *,
        current_user: User,
        title: str,
        file: UploadFile,
    ) -> Resume:
        validate_upload_file(file)
        storage_path = build_storage_path(file.filename or "resume")
        content = file.file.read()
        if not content:
            raise ValueError("Uploaded file is empty.")
        validate_file_size(content)

        storage_path.write_bytes(content)
        try:
            extracted_text = validate_extracted_text(extract_text_from_file(storage_path))
        except Exception:
            if storage_path.exists():
                storage_path.unlink()
            raise

        resume = Resume(
            user_id=current_user.id,
            title=title,
            original_filename=file.filename or storage_path.name,
            file_path=str(storage_path),
            extracted_text=extracted_text,
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        parsing_service.parse_resume(db, resume)
        db.refresh(resume)
        return resume

    def create_job_description(
        self,
        db: Session,
        current_user: User,
        payload: JobDescriptionCreate,
    ) -> JobDescription:
        raw_text = validate_extracted_text(payload.raw_text)
        role_title = payload.role_title.strip()

        job_description = JobDescription(
            user_id=current_user.id,
            company_name=payload.company_name,
            role_title=role_title,
            source_url=payload.source_url,
            raw_text=raw_text,
        )
        db.add(job_description)
        db.commit()
        db.refresh(job_description)
        parsing_service.parse_job_description(db, job_description)
        db.refresh(job_description)
        return job_description


ingestion_service = IngestionService()
