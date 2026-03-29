from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, BaseModelMixin

if TYPE_CHECKING:
    from app.models.answer import Answer


class Evaluation(BaseModelMixin, Base):
    __tablename__ = "evaluations"

    answer_id: Mapped[str] = mapped_column(ForeignKey("answers.id"), nullable=False, index=True)
    score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    correctness_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    clarity_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    completeness_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    semantic_similarity_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    rubric_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    strengths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    improvement_areas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    improvement_suggestions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    answer: Mapped["Answer"] = relationship(back_populates="evaluations")
