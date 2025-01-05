from sqlalchemy.orm import Session

from app.models.mental_health_conversation import MentalHealthConversation
from app.schemas.mental_health_conversation import MentalHealthConversationCreate


def get_conversation(db: Session, conversation_id: int):
    return (
        db.query(MentalHealthConversation)
        .filter(MentalHealthConversation.id == conversation_id)
        .first()
    )


def get_conversations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(MentalHealthConversation).offset(skip).limit(limit).all()


def create_conversation(db: Session, conversation: MentalHealthConversationCreate):
    db_conversation = MentalHealthConversation(
        question=conversation.question, answer=conversation.answer
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


def update_conversation(
    db: Session, conversation_id: int, conversation: MentalHealthConversationCreate
):
    db_conversation = get_conversation(db, conversation_id)
    if db_conversation:
        db_conversation.question = conversation.question
        db_conversation.answer = conversation.answer
        db.commit()
        db.refresh(db_conversation)
    return db_conversation


def delete_conversation(db: Session, conversation_id: int):
    db_conversation = get_conversation(db, conversation_id)
    if db_conversation:
        db.delete(db_conversation)
        db.commit()
        return True
    return False
