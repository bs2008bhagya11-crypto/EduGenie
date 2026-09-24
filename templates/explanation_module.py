import google.generativeai as genai

def get_explanation(concept: str):
    model = genai.GenerativeModel("gemini-pro")

    prompt = f"""
    Explain the following concept in simple and easy-to-understand language:

    {concept}

    Give examples where appropriate.
    """

    response = model.generate_content(prompt)

    return response.text
