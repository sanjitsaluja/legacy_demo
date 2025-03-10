from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import mental_health_conversation
from app.db.database import get_db
from app.schemas.mental_health_conversation import (
    ConversationGenerateRequest,
    ConversationGenerateResponse,
    MentalHealthConversation,
    MentalHealthConversationCreate,
)
from app.services.conversation_generation import ConversationRAGGenerationService
from app.worker.tasks import delete_conversation_index, index_conversation

router = APIRouter()

# Initialize the RAG service
rag_service = ConversationRAGGenerationService()


@router.post("/conversations/", response_model=MentalHealthConversation)
def create_conversation(
    conversation: MentalHealthConversationCreate, db: Session = Depends(get_db)
):
    # Create the conversation in the database
    db_conversation = mental_health_conversation.create_conversation(
        db=db, conversation=conversation
    )

    # Enqueue the indexing task and get the task result
    index_conversation.delay(db_conversation.id)

    return db_conversation


@router.get("/conversations/", response_model=List[MentalHealthConversation])
def read_conversations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    conversations = mental_health_conversation.get_conversations(
        db, skip=skip, limit=limit
    )
    return conversations


@router.get("/conversations/{conversation_id}", response_model=MentalHealthConversation)
def read_conversation(conversation_id: int, db: Session = Depends(get_db)):
    db_conversation = mental_health_conversation.get_conversation(
        db, conversation_id=conversation_id
    )
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return db_conversation


@router.put("/conversations/{conversation_id}", response_model=MentalHealthConversation)
def update_conversation(
    conversation_id: int,
    conversation: MentalHealthConversationCreate,
    db: Session = Depends(get_db),
):
    db_conversation = mental_health_conversation.update_conversation(
        db, conversation_id=conversation_id, conversation=conversation
    )
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Re-index the updated conversation
    index_conversation.delay(conversation_id)

    return db_conversation


@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    success = mental_health_conversation.delete_conversation(
        db, conversation_id=conversation_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Delete from vector index
    delete_conversation_index.delay(conversation_id)

    return {"ok": True}


@router.post("/conversations/generate", response_model=ConversationGenerateResponse)
async def generate_conversation_response(
    request: ConversationGenerateRequest,
):
    """Generate a response for a given question using RAG."""
    try:
        response = rag_service.generate_response(request.question)
        return ConversationGenerateResponse(answer=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
