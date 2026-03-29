from collections import defaultdict
from statistics import mean
from typing import Dict, List, Optional, Union

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.answer import Answer
from app.models.evaluation import Evaluation
from app.models.interview_session import InterviewSession, InterviewSessionStatus
from app.models.question import Question
from app.models.user import User
from app.schemas.analytics import (
    AnalyticsCategoryPerformance,
    AnalyticsSummaryResponse,
    AnalyticsWeakArea,
)


class AnalyticsService:
    _WEAK_AREA_RECOMMENDATIONS = {
        "technical": "Spend more time revising core concepts and explaining implementation tradeoffs aloud.",
        "project-based": "Practice describing project impact with clearer ownership, decisions, and measurable outcomes.",
        "behavioral": "Use a tighter STAR structure and emphasize judgment, collaboration, and results.",
        "hr/general": "Prepare concise role-fit answers that connect your goals to the target position.",
        "correctness": "Anchor answers more directly to the question, role context, and required skills.",
        "clarity": "Improve structure with shorter sections, signposting, and one concrete example.",
        "completeness": "Add depth on actions taken, tools used, and outcomes achieved.",
        "semantic_similarity": "Reuse more job-description and resume language when answering.",
    }

    def _round_metric(self, value: Optional[float]) -> float:
        if value is None:
            return 0.0
        return round(float(value), 2)

    def _build_weak_areas(
        self,
        category_performance: list[AnalyticsCategoryPerformance],
        metric_values: dict[str, float],
    ) -> list[AnalyticsWeakArea]:
        weak_areas: list[AnalyticsWeakArea] = []

        sorted_categories = sorted(category_performance, key=lambda item: item.average_score)
        for category in sorted_categories[:2]:
            if category.questions_attempted == 0 or category.average_score >= 7:
                continue
            weak_areas.append(
                AnalyticsWeakArea(
                    area=category.category,
                    metric="category_score",
                    average_score=self._round_metric(category.average_score),
                    recommendation=self._WEAK_AREA_RECOMMENDATIONS.get(
                        category.category,
                        "Review this category with more targeted interview practice.",
                    ),
                )
            )

        weakest_dimensions = sorted(metric_values.items(), key=lambda item: item[1])
        for metric_name, score in weakest_dimensions[:2]:
            if score >= 7:
                continue
            weak_areas.append(
                AnalyticsWeakArea(
                    area=metric_name.replace("_", " ").title(),
                    metric=metric_name,
                    average_score=self._round_metric(score),
                    recommendation=self._WEAK_AREA_RECOMMENDATIONS.get(
                        metric_name,
                        "Practice this dimension with more targeted mock answers.",
                    ),
                )
            )

        deduped: list[AnalyticsWeakArea] = []
        seen_pairs: set[tuple[str, str]] = set()
        for item in weak_areas:
            key = (item.area, item.metric)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            deduped.append(item)
        return deduped

    def get_summary(self, db: Session, current_user: User) -> AnalyticsSummaryResponse:
        user_id = current_user.id

        # Keep the analytics query logic centralized here so route code stays thin
        # and future dashboard/reporting features can reuse the same summary shape.
        sessions = db.scalars(
            select(InterviewSession)
            .options(
                selectinload(InterviewSession.questions).selectinload(Question.answers),
            )
            .where(InterviewSession.user_id == user_id)
        ).all()
        total_sessions = len(sessions)
        completed_sessions = sum(
            1
            for session in sessions
            if session.status == InterviewSessionStatus.COMPLETED
            or (
                session.questions
                and all(question.answers for question in session.questions)
            )
        )
        questions_generated = (
            db.query(Question)
            .join(InterviewSession, Question.interview_session_id == InterviewSession.id)
            .filter(InterviewSession.user_id == user_id)
            .count()
        )
        answers_submitted = (
            db.query(Answer)
            .join(Question, Answer.question_id == Question.id)
            .join(InterviewSession, Question.interview_session_id == InterviewSession.id)
            .filter(InterviewSession.user_id == user_id)
            .count()
        )
        attempted_question_rows = db.execute(
            select(Question.id)
            .join(Answer, Answer.question_id == Question.id)
            .join(InterviewSession, Question.interview_session_id == InterviewSession.id)
            .where(InterviewSession.user_id == user_id)
        ).all()

        evaluation_rows = db.execute(
            select(Question.category, Evaluation)
            .join(Answer, Evaluation.answer_id == Answer.id)
            .join(Question, Answer.question_id == Question.id)
            .join(InterviewSession, Question.interview_session_id == InterviewSession.id)
            .where(InterviewSession.user_id == user_id)
        ).all()

        questions_attempted = len({question_id for (question_id,) in attempted_question_rows})

        overall_scores: list[float] = []
        correctness_scores: list[float] = []
        clarity_scores: list[float] = []
        completeness_scores: list[float] = []
        similarity_scores: list[float] = []
        category_buckets: Dict[str, Dict[str, Union[List[float], int]]] = defaultdict(
            lambda: {
                "questions_attempted": 0,
                "score": [],
                "correctness": [],
                "clarity": [],
                "completeness": [],
            }
        )

        for category, evaluation in evaluation_rows:
            category_name = category or "uncategorized"
            category_buckets[category_name]["questions_attempted"] += 1

            score = float(evaluation.score or 0)
            correctness = float(evaluation.correctness_score or 0)
            clarity = float(evaluation.clarity_score or 0)
            completeness = float(evaluation.completeness_score or 0)
            similarity = float(evaluation.semantic_similarity_score or 0)

            overall_scores.append(score)
            correctness_scores.append(correctness)
            clarity_scores.append(clarity)
            completeness_scores.append(completeness)
            similarity_scores.append(similarity)

            category_buckets[category_name]["score"].append(score)
            category_buckets[category_name]["correctness"].append(correctness)
            category_buckets[category_name]["clarity"].append(clarity)
            category_buckets[category_name]["completeness"].append(completeness)

        category_performance = [
            AnalyticsCategoryPerformance(
                category=category_name,
                questions_attempted=int(bucket["questions_attempted"]),
                average_score=self._round_metric(mean(bucket["score"]) if bucket["score"] else 0),
                average_correctness=self._round_metric(
                    mean(bucket["correctness"]) if bucket["correctness"] else 0
                ),
                average_clarity=self._round_metric(mean(bucket["clarity"]) if bucket["clarity"] else 0),
                average_completeness=self._round_metric(
                    mean(bucket["completeness"]) if bucket["completeness"] else 0
                ),
            )
            for category_name, bucket in sorted(category_buckets.items())
        ]

        metric_values = {
            "correctness": self._round_metric(mean(correctness_scores) if correctness_scores else 0),
            "clarity": self._round_metric(mean(clarity_scores) if clarity_scores else 0),
            "completeness": self._round_metric(mean(completeness_scores) if completeness_scores else 0),
            "semantic_similarity": self._round_metric(
                mean(similarity_scores) if similarity_scores else 0
            ),
        }

        return AnalyticsSummaryResponse(
            user_id=user_id,
            total_sessions=total_sessions,
            completed_sessions=completed_sessions,
            questions_generated=questions_generated,
            questions_attempted=questions_attempted,
            answers_submitted=answers_submitted,
            average_score=self._round_metric(mean(overall_scores) if overall_scores else 0),
            average_correctness=metric_values["correctness"],
            average_clarity=metric_values["clarity"],
            average_completeness=metric_values["completeness"],
            average_similarity=metric_values["semantic_similarity"],
            category_performance=category_performance,
            weak_areas=self._build_weak_areas(category_performance, metric_values),
        )


analytics_service = AnalyticsService()
