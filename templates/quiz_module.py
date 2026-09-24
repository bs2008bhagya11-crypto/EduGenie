import google.generativeai as genai

def generate_quiz(topic: str):
    model = genai.GenerativeModel("gemini-pro")

    prompt = f"Generate 3 quiz questions about the following topic: {topic}"

    response = model.generate_content(prompt)

    return response.text
