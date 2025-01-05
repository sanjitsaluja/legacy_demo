from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.conversation_generation import ConversationRAGGenerationService

router = APIRouter()


class GenerateResponse(BaseModel):
    response: str


class GenerateRequest(BaseModel):
    query: str


@router.post("/generate", response_model=GenerateResponse)
async def generate_response(
    request: GenerateRequest,
    rag_service: ConversationRAGGenerationService = Depends(
        lambda: ConversationRAGGenerationService()
    ),
) -> GenerateResponse:
    """Generate a response using RAG"""
    response = rag_service.generate_response(request.query)
    return GenerateResponse(response=response)
