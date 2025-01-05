import os

from openai import OpenAI
from pymilvus import MilvusClient

# Initialize clients
milvus_client = MilvusClient(uri="./my_milvus.db")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Collection configuration
COLLECTION_NAME = "qa_collection"
EMBEDDING_DIM = 1536  # OpenAI ada-002 dimension


def get_embedding(text: str) -> list:
    """Get OpenAI embedding for text"""
    response = openai_client.embeddings.create(
        input=text, model="text-embedding-ada-002"
    )
    return response.data[0].embedding


def main():
    # Create collection if it doesn't exist
    if milvus_client.has_collection(COLLECTION_NAME):
        print(f"Collection {COLLECTION_NAME} already exists. Dropping it...")
        milvus_client.drop_collection(COLLECTION_NAME)

    print(f"Creating collection {COLLECTION_NAME}...")
    milvus_client.create_collection(
        collection_name=COLLECTION_NAME,
        dimension=EMBEDDING_DIM,
        primary_field="id",
        vector_field_name="embedding",
    )

    # Sample data
    questions = [
        "What is the capital of France?",
        "How does photosynthesis work?",
        "What is machine learning?",
        "Who wrote Romeo and Juliet?",
    ]

    # Insert data
    print("\nInserting data...")
    data = []
    for i, question in enumerate(questions):
        embedding = get_embedding(question)
        data.append({"id": i, "question": question, "embedding": embedding})

    insert_result = milvus_client.insert(COLLECTION_NAME, data)
    print(f"Inserted {insert_result['insert_count']} records")

    # Search
    print("\nSearching for similar questions to 'What is artificial intelligence?'...")
    search_embedding = get_embedding("What is artificial intelligence?")
    search_results = milvus_client.search(
        collection_name=COLLECTION_NAME,
        data=[search_embedding],
        limit=3,
        output_fields=["question"],
    )

    print("\nTop 3 similar questions:")
    for i, result in enumerate(search_results[0], 1):
        print(
            f"{i}. Question: {result['entity']['question']} (Score: {result['distance']:.4f})"
        )

    # Delete records
    print("\nDeleting all records...")
    delete_result = milvus_client.delete(
        collection_name=COLLECTION_NAME, pks=[0, 1, 2, 3]
    )
    print(f"Deleted {delete_result} records")

    # Drop collection
    print("\nDropping collection...")
    milvus_client.drop_collection(COLLECTION_NAME)
    print("Done!")


if __name__ == "__main__":
    main()
