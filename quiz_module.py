from gemini_client import generate_structured
from schemas import QuizResponse


async def generate_quiz(text: str, count: int = 5) -> QuizResponse:
    prompt = f"""
Create exactly {count} multiple-choice questions from the educational passage.

Rules:
- Exactly four distinct options per question.
- Exactly one correct option.
- correct_answer must exactly match one option.
- Include a short explanation.
- Questions must be answerable from the supplied passage.
- Mix recall, understanding, and application questions where possible.
- Avoid trick questions.
- Return only the requested structured JSON.

Passage:
{text}
""".strip()

    return generate_structured(
        prompt,
        QuizResponse,
        system_instruction=(
            "You are an expert educational assessment designer. "
            "Create fair, unambiguous questions and follow the schema exactly."
        ),
        temperature=0.2,
        max_output_tokens=3000,
    )
