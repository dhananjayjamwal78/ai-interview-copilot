import re


def tokenize_text(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z0-9\+\#\.-]+", text.lower())
        if len(token) > 2
    }


def clamp_score(value: float, minimum: float = 0.0, maximum: float = 10.0) -> float:
    return max(minimum, min(maximum, round(value, 2)))


def jaccard_similarity(left: str, right: str) -> float:
    left_tokens = tokenize_text(left)
    right_tokens = tokenize_text(right)
    if not left_tokens or not right_tokens:
        return 0.0
    intersection = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    if union == 0:
        return 0.0
    return round((intersection / union) * 10, 2)
