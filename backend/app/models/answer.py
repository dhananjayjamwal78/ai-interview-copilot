from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, BaseModelMixin

if TYPE_CHECKING:
    from app.models.evaluation import Evaluation
    from app.models.question import Question


class Answer(BaseModelMixin, Base):
    __tablename__ = "answers"

    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id"), nullable=False, index=True)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)

    question: Mapped["Question"] = relationship(back_populates="answers")
    evaluations: Mapped[list["Evaluation"]] = relationship(
        back_populates="answer",
        cascade="all, delete-orphan",
    )
