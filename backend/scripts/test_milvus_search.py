import os
from typing import List

import openai
from dotenv import load_dotenv
from pymilvus import Collection, connections

# Load environment variables from .env.local
load_dotenv(".env.local")

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_embedding(text: str) -> List[float]:
    """Get embedding from OpenAI API"""
    response = openai.embeddings.create(model="text-embedding-ada-002", input=text)
    return response.data[0].embedding


def search_conversations(query: str, limit: int = 5):
    """Search for similar conversations in Milvus"""
    try:
        # Connect to Milvus
        connections.connect(alias="default", uri=os.getenv("MILVUS_URI"))

        # Get the collection
        collection = Collection(os.getenv("MILVUS_COLLECTION_NAME"))
        collection.load()

        # Get embedding for the query
        query_embedding = get_embedding(query)

        # Search in Milvus
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10},
        }

        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=limit,
            output_fields=["id", "question", "answer"],
        )

        # Print results with more details
        print(f"\nSearch results for query: '{query}'")
        print("-" * 50)
        for hits in results:
            for hit in hits:
                print(f"ID: {hit.entity.get('id')}")
                print(f"Question: {hit.entity.get('question')}")
                print(f"Answer: {hit.entity.get('answer')}")
                print(f"Distance: {hit.distance}")
                print("-" * 30)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        connections.disconnect("default")


if __name__ == "__main__":
    # Example searches
    search_queries = [
        "feeling anxious about work",
        "dealing with depression",
        "relationship problems",
    ]

    for query in search_queries:
        search_conversations(query)
