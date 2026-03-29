from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, BaseModelMixin

if TYPE_CHECKING:
    from app.models.job_description import JobDescription
    from app.models.question import Question
    from app.models.resume import Resume
    from app.models.user import User


class InterviewSessionStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class InterviewSession(BaseModelMixin, Base):
    __tablename__ = "interview_sessions"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    resume_id: Mapped[Optional[str]] = mapped_column(ForeignKey("resumes.id"), nullable=True, index=True)
    job_description_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("job_descriptions.id"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    target_role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    target_skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    question_categories: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[InterviewSessionStatus] = mapped_column(
        SqlEnum(InterviewSessionStatus),
        default=InterviewSessionStatus.DRAFT,
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="interview_sessions")
    resume: Mapped[Optional["Resume"]] = relationship(back_populates="interview_sessions")
    job_description: Mapped[Optional["JobDescription"]] = relationship(
        back_populates="interview_sessions"
    )
    questions: Mapped[list["Question"]] = relationship(
        back_populates="interview_session",
        cascade="all, delete-orphan",
    )
