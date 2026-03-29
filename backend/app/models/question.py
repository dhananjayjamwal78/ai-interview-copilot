from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, BaseModelMixin

if TYPE_CHECKING:
    from app.models.answer import Answer
    from app.models.interview_session import InterviewSession


class Question(BaseModelMixin, Base):
    __tablename__ = "questions"

    interview_session_id: Mapped[str] = mapped_column(
        ForeignKey("interview_sessions.id"),
        nullable=False,
        index=True,
    )
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    interview_session: Mapped["InterviewSession"] = relationship(back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )
