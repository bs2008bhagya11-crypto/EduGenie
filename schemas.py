from typing import Literal
from pydantic import BaseModel, Field, field_validator


def _clean_text(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Input cannot be empty.")
    return value


class TextInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=12000)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return _clean_text(value)


class QARequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=12000)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        return _clean_text(value)


class ExplainRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=1000)

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, value: str) -> str:
        return _clean_text(value)


class QuizRequest(TextInput):
    count: int = Field(default=5, ge=3, le=10)


class SummaryRequest(TextInput):
    style: Literal["quick", "detailed", "exam"] = "quick"


class LearningPathRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=1000)
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    timeframe: str = Field(default="8 weeks", min_length=2, max_length=100)

    @field_validator("topic", "timeframe")
    @classmethod
    def validate_strings(cls, value: str) -> str:
        return _clean_text(value)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=12000)
    history: list[dict[str, str]] = Field(default_factory=list, max_length=20)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        return _clean_text(value)


class TextResponse(BaseModel):
    result: str


class QuizQuestion(BaseModel):
    question: str
    options: list[str] = Field(min_length=4, max_length=4)
    correct_answer: str
    explanation: str


class QuizResponse(BaseModel):
    questions: list[QuizQuestion]


class LearningStep(BaseModel):
    stage: str
    topics: list[str]
    suggested_time: str
    resources: list[str]


class LearningPathResponse(BaseModel):
    topic: str
    level: str
    timeframe: str
    overview: str
    steps: list[LearningStep]
    tips: list[str]


class ChatResponse(BaseModel):
    result: str
