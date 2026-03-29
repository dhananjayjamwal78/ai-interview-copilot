from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, BaseModelMixin

if TYPE_CHECKING:
    from app.models.interview_session import InterviewSession
    from app.models.user import User


class JobDescription(BaseModelMixin, Base):
    __tablename__ = "job_descriptions"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role_title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_requirements: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    required_skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    parsed_role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    parsed_domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    parsed_experience_years: Mapped[Optional[float]] = mapped_column(nullable=True)
    parsed_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    user: Mapped["User"] = relationship(back_populates="job_descriptions")
    interview_sessions: Mapped[list["InterviewSession"]] = relationship(
        back_populates="job_description"
    )
