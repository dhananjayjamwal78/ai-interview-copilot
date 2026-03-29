from sqlalchemy.orm import Session

from app.models.answer import Answer
from app.models.evaluation import Evaluation
from app.models.question import Question
from app.utils.evaluation_helpers import clamp_score, jaccard_similarity, tokenize_text


class EvaluationService:
    def _build_reference_text(self, question: Question) -> str:
        session = question.interview_session
        parts = [question.prompt]
        if session.target_role:
            parts.append(session.target_role)
        if session.target_skills:
            parts.append(" ".join(session.target_skills))
        if session.job_description and session.job_description.extracted_requirements:
            parts.append(" ".join(session.job_description.extracted_requirements[:10]))
        if session.resume and session.resume.parsed_skills:
            parts.append(" ".join(session.resume.parsed_skills))
        return " ".join(part for part in parts if part)

    def _score_correctness(self, answer_text: str, reference_text: str) -> float:
        similarity = jaccard_similarity(answer_text, reference_text)
        return clamp_score(similarity)

    def _score_clarity(self, answer_text: str) -> float:
        words = answer_text.split()
        sentence_count = max(1, answer_text.count(".") + answer_text.count("!") + answer_text.count("?"))
        avg_sentence_length = len(words) / sentence_count if words else 0
        score = 4.0
        if len(words) >= 25:
            score += 2.0
        if len(words) >= 60:
            score += 1.5
        if 8 <= avg_sentence_length <= 28:
            score += 1.5
        if any(marker in answer_text.lower() for marker in ("first", "second", "finally", "because", "for example")):
            score += 1.0
        return clamp_score(score)

    def _score_completeness(self, answer_text: str, reference_text: str) -> float:
        answer_tokens = tokenize_text(answer_text)
        reference_tokens = tokenize_text(reference_text)
        if not answer_tokens:
            return 0.0
        overlap = len(answer_tokens & reference_tokens)
        overlap_score = (overlap / max(1, min(len(reference_tokens), 20))) * 10
        length_bonus = min(len(answer_tokens) / 12, 2.0)
        return clamp_score(overlap_score + length_bonus)

    def _build_feedback(
        self,
        correctness: float,
        clarity: float,
        completeness: float,
        similarity: float,
    ) -> tuple[str, str, str, str]:
        strengths = []
        improvements = []

        if correctness >= 6:
            strengths.append("The answer aligns reasonably well with the expected interview context.")
        else:
            improvements.append("Tie the answer more directly to the question, target role, and required skills.")

        if clarity >= 6:
            strengths.append("The answer is communicated clearly enough to follow.")
        else:
            improvements.append("Use a clearer structure with concise sentences and explicit examples.")

        if completeness >= 6:
            strengths.append("The answer covers multiple relevant points instead of staying too shallow.")
        else:
            improvements.append("Add more concrete details, outcomes, and technical depth.")

        if similarity < 3:
            improvements.append("Use more terminology from the job requirements or your own resume context.")

        rubric_feedback = (
            f"Correctness: {correctness}/10, clarity: {clarity}/10, completeness: {completeness}/10."
        )
        strengths_text = " ".join(strengths) or "The answer is a reasonable first draft."
        improvement_areas = " ".join(improvements) or "Keep refining with tighter examples and outcomes."
        improvement_suggestions = (
            "Use a situation-action-result format, mention relevant tools or skills, and end with a measurable outcome."
        )
        return rubric_feedback, strengths_text, improvement_areas, improvement_suggestions

    def evaluate_answer(self, db: Session, answer: Answer) -> Evaluation:
        question = answer.question
        reference_text = self._build_reference_text(question)
        correctness = self._score_correctness(answer.response_text, reference_text)
        clarity = self._score_clarity(answer.response_text)
        completeness = self._score_completeness(answer.response_text, reference_text)
        similarity = jaccard_similarity(answer.response_text, reference_text)
        overall = clamp_score((correctness * 0.4) + (clarity * 0.25) + (completeness * 0.25) + (similarity * 0.1))
        rubric_feedback, strengths, improvement_areas, improvement_suggestions = self._build_feedback(
            correctness,
            clarity,
            completeness,
            similarity,
        )

        evaluation = Evaluation(
            answer_id=answer.id,
            score=overall,
            correctness_score=correctness,
            clarity_score=clarity,
            completeness_score=completeness,
            semantic_similarity_score=similarity,
            rubric_feedback=rubric_feedback,
            strengths=strengths,
            improvement_areas=improvement_areas,
            improvement_suggestions=improvement_suggestions,
            model_name="deterministic-rubric-v1",
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        return evaluation


evaluation_service = EvaluationService()
