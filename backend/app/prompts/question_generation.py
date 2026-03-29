from app.schemas.generation import QuestionCategory, QuestionDifficulty


def build_question_generation_prompt(
    *,
    source_mode: str,
    categories: list[QuestionCategory],
    difficulty: QuestionDifficulty,
    question_count: int,
    resume_context: str,
    job_description_context: str,
) -> str:
    category_text = ", ".join(categories)
    return f"""
You are an interview question generator for a free local AI interview copilot.

Generate {question_count} interview questions in JSON format.
Use only these categories: {category_text}.
Use this default difficulty level unless context strongly requires otherwise: {difficulty}.
Source mode: {source_mode}.

Return valid JSON only in this shape:
{{
  "questions": [
    {{
      "prompt": "question text",
      "category": "technical or project-based or behavioral or hr/general",
      "difficulty": "easy or medium or hard",
      "suggested_answer": "a concise ideal answer in 40 to 70 words",
      "answer_example": "a very short example line in 15 to 30 words"
    }}
  ]
}}

Resume context:
{resume_context or "Not provided."}

Job description context:
{job_description_context or "Not provided."}

Keep questions tailored, non-repetitive, and specific to the supplied context.
Each suggested answer should be concise, interview-ready, and practical.
Each answer_example should be short and concrete.
""".strip()
