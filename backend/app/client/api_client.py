from typing import Dict, List, Optional

import httpx
from pydantic import BaseModel

from app.schemas.mental_health_conversation import (
    MentalHealthConversation,
    MentalHealthConversationCreate,
)


class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self.client.aclose()

    async def create_conversation(
        self, question: str, answer: str
    ) -> MentalHealthConversation:
        """Create a new conversation."""
        conversation = MentalHealthConversationCreate(question=question, answer=answer)
        response = await self.client.post(
            "/api/v1/conversations/", json=conversation.model_dump()
        )
        response.raise_for_status()
        return MentalHealthConversation.model_validate(response.json())

    async def get_conversation(self, conversation_id: int) -> MentalHealthConversation:
        """Get a specific conversation by ID."""
        response = await self.client.get(f"/api/v1/conversations/{conversation_id}")
        response.raise_for_status()
        return MentalHealthConversation.model_validate(response.json())

    async def get_conversations(
        self, skip: int = 0, limit: int = 100
    ) -> List[MentalHealthConversation]:
        """Get a list of conversations."""
        response = await self.client.get(
            "/api/v1/conversations/", params={"skip": skip, "limit": limit}
        )
        response.raise_for_status()
        return [
            MentalHealthConversation.model_validate(item) for item in response.json()
        ]

    async def update_conversation(
        self, conversation_id: int, question: str, answer: str
    ) -> MentalHealthConversation:
        """Update an existing conversation."""
        conversation = MentalHealthConversationCreate(question=question, answer=answer)
        response = await self.client.put(
            f"/api/v1/conversations/{conversation_id}",
            json=conversation.model_dump(),
        )
        response.raise_for_status()
        return MentalHealthConversation.model_validate(response.json())

    async def delete_conversation(self, conversation_id: int) -> bool:
        """Delete a conversation."""
        response = await self.client.delete(f"/api/v1/conversations/{conversation_id}")
        response.raise_for_status()
        return response.json()["ok"]

    async def generate_conversation_response(self, question: str) -> str:
        """Generate a response for a given question using RAG."""
        response = await self.client.post(
            "/api/v1/conversations/generate", json={"question": question}
        )
        response.raise_for_status()
        return response.json()["answer"]
