from gemini_client import generate_text


async def explain_concept(topic: str) -> str:
    prompt = f"""
Teach the following concept to a student.

Topic:
{topic}

Use this structure:
1. Simple definition
2. Intuition / how it works
3. Step-by-step explanation
4. Easy real-world example
5. Common mistake or misconception
6. One-line revision point

Avoid unnecessary jargon. If technical terms are necessary, define them.
""".strip()

    return generate_text(
        prompt,
        system_instruction=(
            "You are a patient expert teacher. Optimize for understanding, "
            "retention, and exam usefulness."
        ),
        temperature=0.25,
        max_output_tokens=1600,
    )
