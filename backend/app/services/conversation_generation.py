import os
from typing import List

from jinja2 import Environment, FileSystemLoader
from openai import OpenAI
from pydantic import BaseModel

from app.db.milvus_client import milvus_client

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Setup Jinja2 environment
template_env = Environment(loader=FileSystemLoader("app/templates"))


class ConversationContext(BaseModel):
    question: str
    answer: str


class ConversationRAGGenerationService:
    def __init__(self):
        self.template = template_env.get_template("conversation_gen_rag_prompt.jinja")

    def get_similar_conversations(
        self, query: str, limit: int = 3
    ) -> List[ConversationContext]:
        """Retrieve similar conversations from Milvus"""
        # Get embedding for the query
        response = openai_client.embeddings.create(
            input=query, model="text-embedding-ada-002"
        )
        query_embedding = response.data[0].embedding

        # Search in Milvus
        search_results = milvus_client.search(
            collection_name="mental_health_conversations",
            data=[query_embedding],
            limit=limit,
            output_fields=["question", "answer"],
        )

        # Convert results to ConversationContext objects
        conversations = []
        for hit in search_results[0]:
            conversations.append(
                ConversationContext(
                    question=hit["entity"]["question"], answer=hit["entity"]["answer"]
                )
            )

        return conversations

    def generate_response(self, user_query: str) -> str:
        """Generate a response using RAG"""
        # Get similar conversations
        similar_conversations = self.get_similar_conversations(user_query)

        # Prepare prompt using template
        prompt = self.template.render(
            user_query=user_query, similar_conversations=similar_conversations
        )

        # Call OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",  # or your preferred model
            messages=[
                {
                    "role": "system",
                    "content": "You are a mental health counseling assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        return response.choices[0].message.content


if __name__ == "__main__":
    # Test queries
    test_queries = [
        "I've been feeling really anxious about my upcoming job interview",
        "I'm having trouble sleeping due to stress",
        "I can't stop worrying about my relationship",
    ]

    # Initialize service
    rag_service = ConversationRAGGenerationService()

    # Test each query
    for query in test_queries:
        print("\n" + "=" * 50)
        print(f"Test Query: {query}")
        print("=" * 50)

        # Test similar conversations retrieval
        print("\nSimilar Conversations:")
        similar = rag_service.get_similar_conversations(query)
        for idx, conv in enumerate(similar, 1):
            print(f"\nConversation {idx}:")
            print(f"Q: {conv.question}")
            print(f"A: {conv.answer}")

        # Test full response generation
        print("\nGenerated Response:")
        response = rag_service.generate_response(query)
        print(response)
        print("\n" + "=" * 50)
