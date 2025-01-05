from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.crud import mental_health_conversation
from app.schemas.mental_health_conversation import MentalHealthConversationCreate


def test_create_conversation(client: TestClient, db: Session):
    response = client.post(
        "/api/v1/conversations/",
        json={"question": "How are you?", "answer": "I'm good"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "How are you?"
    assert data["answer"] == "I'm good"
    assert "id" in data


def test_read_conversation(client: TestClient, db: Session):
    # Create a conversation first
    conversation = mental_health_conversation.create_conversation(
        db=db,
        conversation=MentalHealthConversationCreate(
            question="Test question", answer="Test answer"
        ),
    )

    response = client.get(f"/api/v1/conversations/{conversation.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "Test question"
    assert data["answer"] == "Test answer"


def test_read_nonexistent_conversation(client: TestClient):
    response = client.get("/api/v1/conversations/999")
    assert response.status_code == 404


def test_update_conversation(client: TestClient, db: Session):
    # Create a conversation first
    conversation = mental_health_conversation.create_conversation(
        db=db,
        conversation=MentalHealthConversationCreate(
            question="Original question", answer="Original answer"
        ),
    )

    response = client.put(
        f"/api/v1/conversations/{conversation.id}",
        json={"question": "Updated question", "answer": "Updated answer"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "Updated question"
    assert data["answer"] == "Updated answer"


def test_delete_conversation(client: TestClient, db: Session):
    # Create a conversation first
    conversation = mental_health_conversation.create_conversation(
        db=db,
        conversation=MentalHealthConversationCreate(
            question="Test question", answer="Test answer"
        ),
    )

    response = client.delete(f"/api/v1/conversations/{conversation.id}")
    assert response.status_code == 200
    assert response.json()["ok"] is True

    # Verify it's deleted
    response = client.get(f"/api/v1/conversations/{conversation.id}")
    assert response.status_code == 404
