import google.generativeai as genai

def get_learning_path(topic: str):
    model = genai.GenerativeModel("gemini-pro")

    prompt = f"Provide a step-by-step learning path for the following topic:\n\n{topic}"

    response = model.generate_content(prompt)

    return response.text
