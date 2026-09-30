from gemini_client import generate_text


async def summarize_text(text: str, style: str = "quick") -> str:
    style_instructions = {
        "quick": "Create a concise revision summary with 5-10 strong bullet points.",
        "detailed": "Create a structured summary with headings, key ideas, and important details.",
        "exam": "Create exam-oriented notes: definitions, key facts, formulas, likely concepts, and a final quick-revision section.",
    }

    prompt = f"""
Summarize the following educational content.

Requested style:
{style_instructions.get(style, style_instructions["quick"])}

Requirements:
- Preserve the important information.
- Remove repetition.
- Do not add unsupported facts.
- Use clear student-friendly language.

Content:
{text}
""".strip()

    return generate_text(
        prompt,
        system_instruction=(
            "You are an educational summarizer. Stay faithful to the supplied material."
        ),
        temperature=0.2,
        max_output_tokens=1800,
    )
