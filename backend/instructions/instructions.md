Here's the corrected and properly formatted Markdown documentation:

# Project Overview

We are building a mental health dataset exploration platform for mental health counselors. This application will allow mental health counselors to search, browse and operate on mental health conversation data. We will start by building the backend.

For this you will use:
- Poetry
- Python
- FastAPI
- Celery with Redis (background workers)
- MySQL
- Redis
- Milvus (Vector DB)
- REST APIs
- SQLAlchemy as ORM
- DotEnv (for environment variables)
- Pydantic for models
- OpenAI for generation and embedding

# Core Functionalities

## 1. Database Setup and CRUD APIs

### 1.1 MySQL DB Setup & Migrations

1. The database name will be `legacy_development`. Save the database name, user, connection information in the env file.

2. We will use Alembic for migrations and keeping track of database changes. First need to generate the migration for the new database table. The table will be called `mental_health_conversations`:

   - `id`: unique pk (integer)
   - `created_at`: datetime (automatically updates when new records are created)
   - `updated_at`: datetime (automatically updates when records are updated)
   - `question`: string
   - `answer`: string 
   - `question_sentiment`: enum (positive or negative or neutral)
   - `answer_sentiment`: enum (positive or negative or neutral)

3. Write the SQL Alchemy ORM for this model.

### 1.2 CRUD APIs 

Write simple CRUD APIs for this database model. The routes should be prefixed with `api/v1/conversations`. The APIs will use the FastAPI framework. Each CRUD API will use the ORM to do the CRUD.

### 1.3 API Client

Write a simple Python API Client for any service to access this API. This way it will be easy for other systems to integrate with the API. Write Pydantic models for parsing API responses so that clients can get models to operate on. These can be exported from the client.

## 2. Data Ingestion

### 2.1 Dataset Format

Our main dataset is a raw CSV file. We will read a CSV dataset from local file system and put that into the MySQL table we just created. The dataset will have 4 fields corresponding to the MySQL table:

- `question`: string
- `answer`: string 
- `question_sentiment`: enum (positive or negative or neutral)
- `answer_sentiment`: enum (positive or negative or neutral)

### 2.2 Data Import Script

Write a script that reads the CSV and inserts records into the table we just created. Use the API client to create records (not the ORM).

### 2.3 Vector Database Indexing via Celery

#### 2.3.1 Milvus Setup

Since we will use LLMs and RAG with this data, we need to create a collection in our Milvus vector database. The collection will be called `mental_health_embeddings_development`. In the Milvus vector db, we will save:

- `id` (id of the conversation from MySQL)
- `embedding`
- `question`: string
- `question_sentiment`: string

#### 2.3.2 Celery Workers

We will create 3 Celery workers that will operate on the vector database. The Celery workers should take the primary key ID of the record created:

- `CreatedMentalHealthConversationJob`: Inserts data into the Milvus collection using the ID as PK
- `UpdatedMentalHealthConversationJob`: Updates data in the Milvus collection using the ID
- `DeletedMentalHealthConversationJob`: Deletes the data in the Milvus collection using the ID

#### 2.3.3 API Integration

Update the REST APIs to queue the respective Celery workers after the record is committed to the database.

## 3. RAG Search and Generation

### 3.1 OpenAI and RAG Generation Service

Users can enter free-text that describes the challenge they are facing with a particular patient, invoke the LLM using the user's input, and return a suggestion on how to best help the patient.

#### 3.1.1 Service Implementation

Build a service that takes a string question:
1. Searches the vector database for the top 3 hits based on the input question
2. Retrieves both the question and the answer for the top 3 hits
3. Creates a startup prompt in a Jinja file
4. Uses the questions and answers from the vector database to fill out a prompt
5. Sends the prompt to OpenAI and returns the generated response to the user

### 3.2 API Endpoint

Build an API which takes an incoming user question as JSON body text. It then uses the service above and returns the answer to the user.

# Documentation

## Milvus Usage Example

```python
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
```

# Existing project structure

.
├── docker-compose.yml
├── my_milvus.db
└── train.csv
└── .env.local
