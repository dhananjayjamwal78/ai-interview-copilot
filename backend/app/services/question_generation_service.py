import json
import re
from typing import Any

from sqlalchemy.orm import Session

from app.models.interview_session import InterviewSession, InterviewSessionStatus
from app.models.job_description import JobDescription
from app.models.question import Question
from app.models.resume import Resume
from app.models.user import User
from app.prompts import build_question_generation_prompt
from app.schemas.generation import (
    GeneratedQuestionItem,
    QuestionGenerationRequest,
    QuestionGenerationResponse,
)
from app.services.llm_service import LLMProviderError, llm_service


class QuestionGenerationService:
    _CATEGORY_ALIASES = {
        "technical": "technical",
        "tech": "technical",
        "project-based": "project-based",
        "project based": "project-based",
        "project": "project-based",
        "behavioral": "behavioral",
        "behavioural": "behavioral",
        "hr/general": "hr/general",
        "hr": "hr/general",
        "general": "hr/general",
        "hr general": "hr/general",
    }
    _DIFFICULTY_ALIASES = {
        "easy": "easy",
        "medium": "medium",
        "moderate": "medium",
        "hard": "hard",
        "difficult": "hard",
    }

    def _build_resume_context(self, resume: Resume) -> str:
        return (
            f"Title: {resume.title}\n"
            f"Skills: {', '.join(resume.parsed_skills)}\n"
            f"Roles: {', '.join(resume.parsed_roles)}\n"
            f"Domains: {', '.join(resume.parsed_domains)}\n"
            f"Experience Years: {resume.parsed_experience_years}\n"
            f"Excerpt: {(resume.extracted_text or '')[:1500]}"
        )

    def _build_job_description_context(self, job_description: JobDescription) -> str:
        return (
            f"Role Title: {job_description.role_title}\n"
            f"Company: {job_description.company_name or 'Unknown'}\n"
            f"Required Skills: {', '.join(job_description.required_skills)}\n"
            f"Preferred Skills: {', '.join(job_description.preferred_skills)}\n"
            f"Requirements: {' | '.join(job_description.extracted_requirements[:8])}\n"
            f"Excerpt: {job_description.raw_text[:1500]}"
        )

    def _extract_json_payload(self, text: str) -> dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Some local model outputs wrap the JSON in extra prose. We recover the
            # first JSON object so the higher-level workflow can stay deterministic.
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                raise ValueError("LLM response did not contain valid JSON.")
            return json.loads(match.group(0))

    def _normalize_category(self, raw_value: Any, fallback_category: str) -> str:
        if raw_value is None:
            return fallback_category

        cleaned = str(raw_value).strip().lower()
        if not cleaned:
            return fallback_category

        direct_match = self._CATEGORY_ALIASES.get(cleaned)
        if direct_match:
            return direct_match

        fragments = re.split(r"[/|,;]|(?:\s+-\s+)|(?:\s+and\s+)", cleaned)
        for fragment in fragments:
            normalized = self._CATEGORY_ALIASES.get(fragment.strip())
            if normalized:
                return normalized

        for alias, canonical in self._CATEGORY_ALIASES.items():
            if alias in cleaned:
                return canonical

        return fallback_category

    def _normalize_difficulty(self, raw_value: Any, fallback_difficulty: str) -> str:
        if raw_value is None:
            return fallback_difficulty

        cleaned = str(raw_value).strip().lower()
        if not cleaned:
            return fallback_difficulty

        direct_match = self._DIFFICULTY_ALIASES.get(cleaned)
        if direct_match:
            return direct_match

        for alias, canonical in self._DIFFICULTY_ALIASES.items():
            if alias in cleaned:
                return canonical

        return fallback_difficulty

    def _normalize_questions(
        self,
        payload: dict[str, Any],
        fallback_categories: list[str],
        fallback_difficulty: str,
        question_count: int,
    ) -> list[GeneratedQuestionItem]:
        raw_questions = payload.get("questions", [])
        if not isinstance(raw_questions, list) or not raw_questions:
            raise ValueError("LLM response did not include a valid questions list.")

        normalized = []
        for index, item in enumerate(raw_questions[:question_count]):
            if not isinstance(item, dict) or not item.get("prompt"):
                continue
            fallback_category = fallback_categories[index % len(fallback_categories)]
            category = self._normalize_category(item.get("category"), fallback_category)
            difficulty = self._normalize_difficulty(
                item.get("difficulty"),
                fallback_difficulty,
            )
            normalized.append(
                GeneratedQuestionItem(
                    prompt=str(item["prompt"]).strip(),
                    category=category,
                    difficulty=difficulty,
                    suggested_answer=str(
                        item.get("suggested_answer")
                        or "Start with a direct answer, add one concrete detail, and close with the impact."
                    ).strip(),
                    answer_example=str(
                        item.get("answer_example")
                        or "For example, I improved reliability by simplifying the deployment flow and adding monitoring."
                    ).strip(),
                )
            )
        if not normalized:
            raise ValueError("No usable questions were returned by the provider.")
        return normalized

    def _resolve_context(
        self,
        db: Session,
        current_user: User,
        payload: QuestionGenerationRequest,
    ) -> tuple[InterviewSession, str, str, str]:
        if payload.interview_session_id:
            interview_session = db.get(InterviewSession, payload.interview_session_id)
            if interview_session is None or interview_session.user_id != current_user.id:
                raise ValueError("Interview session not found.")
            resume = interview_session.resume
            job_description = interview_session.job_description
            source_mode = "existing_session"
        else:
            resume = db.get(Resume, payload.resume_id) if payload.resume_id else None
            job_description = (
                db.get(JobDescription, payload.job_description_id)
                if payload.job_description_id
                else None
            )
            if resume is None and job_description is None:
                raise ValueError("Resume or job description context is required.")
            if resume and resume.user_id != current_user.id:
                raise ValueError("Resume does not belong to the authenticated user.")
            if job_description and job_description.user_id != current_user.id:
                raise ValueError("Job description does not belong to the authenticated user.")
            if resume and job_description and resume.user_id != job_description.user_id:
                raise ValueError("Resume and job description must belong to the same user.")

            user_id = current_user.id
            interview_session = InterviewSession(
                user_id=user_id,
                resume_id=resume.id if resume else None,
                job_description_id=job_description.id if job_description else None,
                title=payload.session_title
                or (
                    f"Generated interview for {job_description.role_title}"
                    if job_description
                    else f"Generated interview for {resume.title}"
                ),
                status=InterviewSessionStatus.READY,
            )
            db.add(interview_session)
            db.flush()

            if resume and job_description:
                source_mode = "resume_and_jd"
            elif resume:
                source_mode = "resume_only"
            else:
                source_mode = "jd_only"

        resume_context = self._build_resume_context(resume) if resume else ""
        jd_context = self._build_job_description_context(job_description) if job_description else ""
        return interview_session, source_mode, resume_context, jd_context

    def generate_questions(
        self,
        db: Session,
        current_user: User,
        payload: QuestionGenerationRequest,
    ) -> QuestionGenerationResponse:
        (
            interview_session,
            source_mode,
            resume_context,
            job_description_context,
        ) = self._resolve_context(db, current_user, payload)

        prompt = build_question_generation_prompt(
            source_mode=source_mode,
            categories=payload.categories,
            difficulty=payload.difficulty,
            question_count=payload.question_count,
            resume_context=resume_context,
            job_description_context=job_description_context,
        )

        try:
            llm_output = llm_service.generate(prompt)
        except LLMProviderError as exc:
            raise ValueError(str(exc)) from exc

        parsed_payload = self._extract_json_payload(llm_output)
        questions = self._normalize_questions(
            parsed_payload,
            payload.categories,
            payload.difficulty,
            payload.question_count,
        )

        interview_session.questions.clear()
        interview_session.question_categories = list(payload.categories)
        if not interview_session.target_role:
            interview_session.target_role = (
                interview_session.job_description.role_title
                if interview_session.job_description
                else None
            )
        inferred_skills = []
        if interview_session.resume:
            inferred_skills.extend(interview_session.resume.parsed_skills)
        if interview_session.job_description:
            inferred_skills.extend(interview_session.job_description.required_skills)
        if inferred_skills:
            interview_session.target_skills = list(dict.fromkeys(inferred_skills))
        for index, item in enumerate(questions, start=1):
            interview_session.questions.append(
                Question(
                    interview_session_id=interview_session.id,
                    prompt=item.prompt,
                    category=item.category,
                    difficulty=item.difficulty,
                    display_order=index,
                )
            )
        interview_session.status = InterviewSessionStatus.READY
        db.add(interview_session)
        db.commit()
        db.refresh(interview_session)

        return QuestionGenerationResponse(
            interview_session_id=interview_session.id,
            source_mode=source_mode,
            generated_count=len(questions),
            questions=questions,
            provider=llm_service.provider.provider_name,
            model=llm_service.provider.model_name,
        )


question_generation_service = QuestionGenerationService()
