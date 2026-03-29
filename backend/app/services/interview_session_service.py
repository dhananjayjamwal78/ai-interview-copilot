from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.answer import Answer
from app.models.evaluation import Evaluation
from app.models.interview_session import InterviewSession, InterviewSessionStatus
from app.models.job_description import JobDescription
from app.models.question import Question
from app.models.resume import Resume
from app.models.user import User
from app.schemas.session import (
    InterviewSessionCreateRequest,
    InterviewSessionDetail,
    InterviewSessionSummary,
)
from app.schemas.session_view import (
    SessionAnswerView,
    SessionEvaluationView,
    SessionQuestionView,
)


class InterviewSessionService:
    def _build_summary(self, session: InterviewSession) -> InterviewSessionSummary:
        return InterviewSessionSummary(
            id=session.id,
            user_id=session.user_id,
            resume_id=session.resume_id,
            job_description_id=session.job_description_id,
            title=session.title,
            target_role=session.target_role,
            target_skills=session.target_skills,
            question_categories=session.question_categories,
            status=session.status.value,
            started_at=session.started_at,
            completed_at=session.completed_at,
            created_at=session.created_at,
            updated_at=session.updated_at,
            question_count=len(session.questions),
        )

    def _build_detail(self, session: InterviewSession) -> InterviewSessionDetail:
        return InterviewSessionDetail(
            **self._build_summary(session).model_dump(),
            notes=session.notes,
            questions=[
                SessionQuestionView(
                    id=question.id,
                    prompt=question.prompt,
                    category=question.category,
                    difficulty=question.difficulty,
                    display_order=question.display_order,
                    answers=[
                        SessionAnswerView(
                            id=answer.id,
                            response_text=answer.response_text,
                            created_at=answer.created_at,
                            updated_at=answer.updated_at,
                            evaluations=[
                                SessionEvaluationView(
                                    id=evaluation.id,
                                    score=float(evaluation.score)
                                    if evaluation.score is not None
                                    else None,
                                    correctness_score=float(evaluation.correctness_score)
                                    if evaluation.correctness_score is not None
                                    else None,
                                    clarity_score=float(evaluation.clarity_score)
                                    if evaluation.clarity_score is not None
                                    else None,
                                    completeness_score=float(evaluation.completeness_score)
                                    if evaluation.completeness_score is not None
                                    else None,
                                    semantic_similarity_score=float(
                                        evaluation.semantic_similarity_score
                                    )
                                    if evaluation.semantic_similarity_score is not None
                                    else None,
                                    rubric_feedback=evaluation.rubric_feedback,
                                    strengths=evaluation.strengths,
                                    improvement_areas=evaluation.improvement_areas,
                                    improvement_suggestions=evaluation.improvement_suggestions,
                                    model_name=evaluation.model_name,
                                    created_at=evaluation.created_at,
                                )
                                for evaluation in answer.evaluations
                            ],
                        )
                        for answer in answer_sort(question.answers)
                    ],
                )
                for question in sorted(session.questions, key=lambda item: item.display_order)
            ],
        )

    def _resolve_user_id(
        self,
        db: Session,
        current_user: User,
        payload: InterviewSessionCreateRequest,
    ) -> Tuple[str, Optional[Resume], Optional[JobDescription]]:
        resume = db.get(Resume, payload.resume_id) if payload.resume_id else None
        job_description = (
            db.get(JobDescription, payload.job_description_id)
            if payload.job_description_id
            else None
        )

        if payload.resume_id and resume is None:
            raise ValueError("Resume not found.")
        if payload.job_description_id and job_description is None:
            raise ValueError("Job description not found.")

        user_id = current_user.id

        if resume and resume.user_id != user_id:
            raise ValueError("Resume does not belong to the authenticated user.")
        if job_description and job_description.user_id != user_id:
            raise ValueError("Job description does not belong to the authenticated user.")

        return user_id, resume, job_description

    def create_session(
        self,
        db: Session,
        current_user: User,
        payload: InterviewSessionCreateRequest,
    ) -> InterviewSessionDetail:
        user_id, resume, job_description = self._resolve_user_id(
            db, current_user, payload
        )

        title = payload.title or (
            f"{payload.target_role or (job_description.role_title if job_description else 'Interview Session')}"
        )
        target_role = payload.target_role or (
            job_description.role_title if job_description else None
        )
        inferred_skills = []
        if resume:
            inferred_skills.extend(resume.parsed_skills)
        if job_description:
            inferred_skills.extend(job_description.required_skills)
        target_skills = payload.target_skills or list(dict.fromkeys(inferred_skills))

        session = InterviewSession(
            user_id=user_id,
            resume_id=resume.id if resume else None,
            job_description_id=job_description.id if job_description else None,
            title=title,
            target_role=target_role,
            target_skills=target_skills,
            question_categories=list(payload.question_categories),
            notes=payload.notes,
            status=InterviewSessionStatus.DRAFT,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return self._build_detail(session)

    def list_sessions(
        self,
        db: Session,
        user_id: str,
    ) -> list[InterviewSessionSummary]:
        statement = (
            select(InterviewSession)
            .options(
                selectinload(InterviewSession.questions)
                .selectinload(Question.answers)
                .selectinload(Answer.evaluations)
            )
            .order_by(InterviewSession.created_at.desc())
        )
        statement = statement.where(InterviewSession.user_id == user_id)
        sessions = db.scalars(statement).all()
        return [self._build_summary(session) for session in sessions]

    def get_session(
        self,
        db: Session,
        user_id: str,
        session_id: str,
    ) -> Optional[InterviewSessionDetail]:
        statement = (
            select(InterviewSession)
            .options(
                selectinload(InterviewSession.questions)
                .selectinload(Question.answers)
                .selectinload(Answer.evaluations)
            )
            .where(InterviewSession.user_id == user_id)
            .where(InterviewSession.id == session_id)
        )
        session = db.scalar(statement)
        if session is None:
            return None
        return self._build_detail(session)


def answer_sort(answers: list[Answer]) -> list[Answer]:
    return sorted(answers, key=lambda item: item.created_at)


interview_session_service = InterviewSessionService()
