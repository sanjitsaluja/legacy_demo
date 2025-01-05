import asyncio

from app.client.api_client import APIClient


async def main():
    async with APIClient() as client:
        # Create a new conversation
        conversation = await client.create_conversation(
            question="How are you feeling today?",
            answer="I'm feeling pretty good, thank you for asking.",
        )
        print(f"Created conversation: {conversation}")

        # Get all conversations
        conversations = await client.get_conversations()
        print(f"All conversations: {conversations}")

        # Get a specific conversation
        conversation = await client.get_conversation(conversation.id)
        print(f"Retrieved conversation: {conversation}")

        # Update the conversation
        updated = await client.update_conversation(
            conversation.id,
            question="How are you really feeling?",
            answer="I'm actually feeling a bit anxious.",
        )
        print(f"Updated conversation: {updated}")

        # Delete the conversation
        deleted = await client.delete_conversation(conversation.id)
        print(f"Deleted conversation: {deleted}")


if __name__ == "__main__":
    asyncio.run(main())
