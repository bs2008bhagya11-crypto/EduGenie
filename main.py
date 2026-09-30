from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import settings
from schemas import (
    ExplainRequest,
    QARequest,
    QuizRequest,
    SummaryRequest,
    LearningPathRequest,
    ChatRequest,
    TextResponse,
    QuizResponse,
    LearningPathResponse,
    ChatResponse,
)
from qna import answer_question
from explanation_module import explain_concept
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations
from gemini_client import generate_text


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Advanced Gemini Flash powered educational learning assistant.",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_name": settings.app_name},
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "gemini_configured": bool(settings.gemini_api_key),
        "model": settings.gemini_model,
    }


@app.post("/qa", response_model=TextResponse)
async def qa(payload: QARequest):
    return TextResponse(result=await answer_question(payload.question))


@app.post("/explain", response_model=TextResponse)
async def explain(payload: ExplainRequest):
    return TextResponse(result=await explain_concept(payload.topic))


@app.post("/quiz", response_model=QuizResponse)
async def quiz(payload: QuizRequest):
    return await generate_quiz(payload.text, payload.count)


@app.post("/summarize", response_model=TextResponse)
async def summarize(payload: SummaryRequest):
    return TextResponse(result=await summarize_text(payload.text, payload.style))


@app.post("/learn/recommendations", response_model=LearningPathResponse)
async def learning_recommendations(payload: LearningPathRequest):
    return await get_learning_recommendations(
        topic=payload.topic,
        level=payload.level,
        timeframe=payload.timeframe,
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    history_text = "\n".join(
        f"{item.get('role', 'user').upper()}: {item.get('content', '')}"
        for item in payload.history[-20:]
    )

    prompt = f"""
Continue this educational tutoring conversation.

Conversation history:
{history_text or "(No previous messages)"}

Student:
{payload.message}

Respond as EduGenie. Maintain context, explain clearly, and help the student
learn rather than simply giving unexplained answers.
""".strip()

    return ChatResponse(
        result=generate_text(
            prompt,
            system_instruction=(
                "You are EduGenie, a friendly expert AI tutor powered by Gemini Flash."
            ),
            temperature=0.35,
            max_output_tokens=1800,
        )
    )
