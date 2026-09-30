import pytest
from fastapi.testclient import TestClient

import main
from schemas import LearningPathResponse, QuizResponse, QuizQuestion, LearningStep

client = TestClient(main.app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "model" in response.json()


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "EduGenie" in response.text
    assert "Gemini Flash" in response.text


@pytest.mark.parametrize(
    ("path", "payload", "monkey_name"),
    [
        ("/qa", {"question": "What is gravity?"}, "answer_question"),
        ("/explain", {"topic": "gravity"}, "explain_concept"),
        ("/summarize", {"text": "A short passage about gravity."}, "summarize_text"),
    ],
)
def test_text_endpoints(monkeypatch, path, payload, monkey_name):
    async def fake(*args, **kwargs):
        return "Mock educational response."

    monkeypatch.setattr(main, monkey_name, fake)
    response = client.post(path, json=payload)

    assert response.status_code == 200
    assert response.json()["result"] == "Mock educational response."


def test_quiz(monkeypatch):
    async def fake_quiz(text, count=5):
        return QuizResponse(
            questions=[
                QuizQuestion(
                    question="What is 2 + 2?",
                    options=["1", "2", "3", "4"],
                    correct_answer="4",
                    explanation="Adding two and two gives four.",
                )
            ]
        )

    monkeypatch.setattr(main, "generate_quiz", fake_quiz)
    response = client.post(
        "/quiz",
        json={"text": "Basic arithmetic.", "count": 5},
    )

    assert response.status_code == 200
    assert response.json()["questions"][0]["correct_answer"] == "4"


def test_learning_path(monkeypatch):
    async def fake_path(topic, level, timeframe):
        return LearningPathResponse(
            topic=topic,
            level=level,
            timeframe=timeframe,
            overview="Mock plan.",
            steps=[
                LearningStep(
                    stage="Foundations",
                    topics=["Basics"],
                    suggested_time="1 week",
                    resources=["Official documentation"],
                )
            ],
            tips=["Practice daily."],
        )

    monkeypatch.setattr(main, "get_learning_recommendations", fake_path)
    response = client.post(
        "/learn/recommendations",
        json={"topic": "SQL", "level": "beginner", "timeframe": "8 weeks"},
    )

    assert response.status_code == 200
    assert response.json()["topic"] == "SQL"


def test_chat(monkeypatch):
    def fake_generate(*args, **kwargs):
        return "Hello student."

    monkeypatch.setattr(main, "generate_text", fake_generate)
    response = client.post(
        "/chat",
        json={"message": "Explain variables simply.", "history": []},
    )

    assert response.status_code == 200
    assert response.json()["result"] == "Hello student."


def test_validation_rejects_empty_question():
    response = client.post("/qa", json={"question": " "})
    assert response.status_code == 422
