from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, BaseModelMixin

if TYPE_CHECKING:
    from app.models.interview_session import InterviewSession
    from app.models.job_description import JobDescription
    from app.models.resume import Resume


class User(BaseModelMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    resumes: Mapped[list["Resume"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    job_descriptions: Mapped[list["JobDescription"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    interview_sessions: Mapped[list["InterviewSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
