import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.client.api_client import APIClient


@pytest.mark.asyncio
async def test_api_client():
    async with APIClient() as client:
        # Test create conversation
        conversation = await client.create_conversation(
            question="Test question",
            answer="Test answer",
        )
        assert conversation.question == "Test question"
        assert conversation.answer == "Test answer"
        assert conversation.id is not None

        # Test get conversation
        retrieved = await client.get_conversation(conversation.id)
        assert retrieved.id == conversation.id
        assert retrieved.question == conversation.question
        assert retrieved.answer == conversation.answer

        # Test update conversation
        updated = await client.update_conversation(
            conversation.id,
            question="Updated question",
            answer="Updated answer",
        )
        assert updated.id == conversation.id
        assert updated.question == "Updated question"
        assert updated.answer == "Updated answer"

        # Test get conversations
        conversations = await client.get_conversations()
        assert len(conversations) > 0
        assert any(c.id == conversation.id for c in conversations)

        # Test delete conversation
        deleted = await client.delete_conversation(conversation.id)
        assert deleted is True

        # Verify deletion
        with pytest.raises(Exception):
            await client.get_conversation(conversation.id)
