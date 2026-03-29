from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, BaseModelMixin

if TYPE_CHECKING:
    from app.models.interview_session import InterviewSession
    from app.models.user import User


class Resume(BaseModelMixin, Base):
    __tablename__ = "resumes"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parsed_skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    parsed_roles: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    parsed_domains: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    parsed_experience_years: Mapped[Optional[float]] = mapped_column(nullable=True)
    parsed_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    user: Mapped["User"] = relationship(back_populates="resumes")
    interview_sessions: Mapped[list["InterviewSession"]] = relationship(
        back_populates="resume"
    )
