from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.chatbot_llm_service import ask_limited_context_chatbot


router = APIRouter(
    prefix="/chatbot",
    tags=["chatbot"],
)

api_router = APIRouter(
    prefix="/api/chatbot",
    tags=["chatbot"],
)


class ChatbotQuestionIn(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000)


class ChatbotAnswerOut(BaseModel):
    answer: str
    matched_intent: str | None = None
    confidence: float


@router.post("/guest/ask", response_model=ChatbotAnswerOut)
def ask_guest_chatbot(payload: ChatbotQuestionIn):
    try:
        result = ask_limited_context_chatbot(payload.question)
        return ChatbotAnswerOut(
            answer=result["answer"],
            matched_intent=result.get("topic_id"),
            confidence=round(float(result.get("confidence", 0.0)), 3),
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Chatbot unavailable: {str(exc)}")


@api_router.post("/guest/ask", response_model=ChatbotAnswerOut)
def ask_guest_chatbot_api(payload: ChatbotQuestionIn):
    return ask_guest_chatbot(payload)
