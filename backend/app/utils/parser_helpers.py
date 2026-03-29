import re
from typing import Iterable, Optional


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def find_keyword_matches(text: str, keywords: Iterable[str]) -> list[str]:
    normalized = text.lower()
    matches = []
    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
        if re.search(pattern, normalized) and keyword not in matches:
            matches.append(keyword)
    return matches


def extract_experience_years(text: str) -> Optional[float]:
    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s+years? of experience",
        r"experience of\s+(\d+(?:\.\d+)?)\+?\s+years?",
        r"(\d+(?:\.\d+)?)\+?\s+yrs? experience",
    ]
    normalized = text.lower()
    values = []
    for pattern in patterns:
        for match in re.findall(pattern, normalized):
            try:
                values.append(float(match))
            except ValueError:
                continue
    return max(values) if values else None


def split_lines(text: str) -> list[str]:
    return [line.strip(" -\t") for line in text.splitlines() if line.strip()]
