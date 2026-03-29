from sqlalchemy.orm import Session

from app.models.job_description import JobDescription
from app.models.resume import Resume
from app.schemas.parsing import JobDescriptionParsedData, ResumeParsedData
from app.utils.parser_helpers import (
    extract_experience_years,
    find_keyword_matches,
    normalize_whitespace,
    split_lines,
)
from app.utils.parsing_rules import (
    DOMAIN_KEYWORDS,
    PREFERRED_PREFIXES,
    REQUIREMENT_PREFIXES,
    ROLE_KEYWORDS,
    SKILL_KEYWORDS,
)


class DeterministicResumeParser:
    def parse(self, text: str) -> ResumeParsedData:
        normalized = normalize_whitespace(text)
        skills = find_keyword_matches(normalized, SKILL_KEYWORDS)
        roles = find_keyword_matches(normalized, ROLE_KEYWORDS)
        domains = find_keyword_matches(normalized, DOMAIN_KEYWORDS)
        experience_years = extract_experience_years(normalized)
        metadata = {
            "parser": "deterministic",
            "text_length": len(normalized),
            "skill_count": len(skills),
            "role_count": len(roles),
            "domain_count": len(domains),
        }
        return ResumeParsedData(
            skills=skills,
            roles=roles,
            domains=domains,
            experience_years=experience_years,
            metadata=metadata,
        )


class DeterministicJobDescriptionParser:
    def parse(self, text: str, fallback_role: str = "") -> JobDescriptionParsedData:
        normalized = normalize_whitespace(text)
        lines = split_lines(text)
        all_skills = find_keyword_matches(normalized, SKILL_KEYWORDS)
        preferred_lines = [
            line for line in lines if line.lower().startswith(PREFERRED_PREFIXES)
        ]
        requirement_lines = [
            line for line in lines if line.lower().startswith(REQUIREMENT_PREFIXES)
        ]
        preferred_text = " ".join(preferred_lines)
        required_skills = [
            skill for skill in all_skills if skill not in find_keyword_matches(preferred_text, all_skills)
        ]
        preferred_skills = find_keyword_matches(preferred_text, all_skills)
        roles = find_keyword_matches(normalized, ROLE_KEYWORDS)
        domains = find_keyword_matches(normalized, DOMAIN_KEYWORDS)
        experience_years = extract_experience_years(normalized)
        metadata = {
            "parser": "deterministic",
            "text_length": len(normalized),
            "requirements_count": len(requirement_lines),
            "required_skill_count": len(required_skills),
            "preferred_skill_count": len(preferred_skills),
        }
        return JobDescriptionParsedData(
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            requirements=requirement_lines,
            role=roles[0] if roles else (fallback_role or None),
            domain=domains[0] if domains else None,
            experience_years=experience_years,
            metadata=metadata,
        )


class ParsingService:
    def __init__(self) -> None:
        self.resume_parser = DeterministicResumeParser()
        self.job_description_parser = DeterministicJobDescriptionParser()

    def parse_resume(self, db: Session, resume: Resume) -> ResumeParsedData:
        if not resume.extracted_text:
            raise ValueError("Resume does not contain extracted text to parse.")

        parsed = self.resume_parser.parse(resume.extracted_text)
        resume.parsed_skills = parsed.skills
        resume.parsed_roles = parsed.roles
        resume.parsed_domains = parsed.domains
        resume.parsed_experience_years = parsed.experience_years
        resume.parsed_metadata = parsed.metadata
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return parsed

    def parse_job_description(
        self,
        db: Session,
        job_description: JobDescription,
    ) -> JobDescriptionParsedData:
        parsed = self.job_description_parser.parse(
            job_description.raw_text,
            fallback_role=job_description.role_title,
        )
        job_description.extracted_requirements = parsed.requirements
        job_description.required_skills = parsed.required_skills
        job_description.preferred_skills = parsed.preferred_skills
        job_description.parsed_role = parsed.role
        job_description.parsed_domain = parsed.domain
        job_description.parsed_experience_years = parsed.experience_years
        job_description.parsed_metadata = parsed.metadata
        db.add(job_description)
        db.commit()
        db.refresh(job_description)
        return parsed


parsing_service = ParsingService()
