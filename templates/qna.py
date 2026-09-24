import google.generativeai as genai

def get_qna_answer(question: str):
    model = genai.GenerativeModel("gemini-pro")

    prompt = f"Answer the following question clearly and accurately:\n\n{question}"

    response = model.generate_content(prompt)

    return response.text
