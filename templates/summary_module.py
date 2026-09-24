import google.generativeai as genai

def get_summary(text: str):
    model = genai.GenerativeModel("gemini-pro")

    prompt = f"Summarize the following text in simple language:\n\n{text}"

    response = model.generate_content(prompt)

    return response.text
