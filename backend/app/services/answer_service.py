from datetime import datetime, timezone

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app.models.answer import Answer
from app.models.interview_session import InterviewSession, InterviewSessionStatus
from app.models.question import Question
from app.models.user import User
from app.schemas.evaluation import AnswerSubmissionRequest
from app.services.evaluation_service import evaluation_service


class AnswerService:
    def _update_session_status(self, db: Session, session: InterviewSession) -> None:
        answered_questions = sum(1 for question in session.questions if question.answers)
        total_questions = len(session.questions)

        if total_questions and answered_questions >= total_questions:
            session.status = InterviewSessionStatus.COMPLETED
            session.completed_at = datetime.now(timezone.utc)
        else:
            session.status = InterviewSessionStatus.IN_PROGRESS
            session.completed_at = None

        db.add(session)
        db.commit()

    def submit_answer(
        self,
        db: Session,
        current_user: User,
        payload: AnswerSubmissionRequest,
    ) -> tuple[Answer, object]:
        statement = (
            select(Question)
            .options(
                selectinload(Question.interview_session).selectinload(InterviewSession.resume),
                selectinload(Question.interview_session).selectinload(InterviewSession.job_description),
            )
            .where(Question.id == payload.question_id)
        )
        question = db.scalar(statement)
        if question is None or question.interview_session.user_id != current_user.id:
            raise ValueError("Question not found.")

        response_text = payload.response_text.strip()
        if not response_text:
            raise ValueError("Answer text cannot be empty.")

        answer = Answer(
            question_id=payload.question_id,
            response_text=response_text,
        )
        db.add(answer)
        db.commit()
        db.refresh(answer)

        answer = db.scalar(
            select(Answer)
            .options(
                selectinload(Answer.question)
                .selectinload(Question.interview_session)
                .selectinload(InterviewSession.questions)
                .selectinload(Question.answers)
            )
            .where(Answer.id == answer.id)
        )
        evaluation = evaluation_service.evaluate_answer(db, answer)
        self._update_session_status(db, answer.question.interview_session)
        return answer, evaluation


answer_service = AnswerService()
