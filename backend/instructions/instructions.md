# Mental Health Dataset Exploration Platform - PRD

## 1. Introduction

We are building a mental health dataset exploration platform for mental health counselors. This application will allow mental health counselors to search, browse, and operate on mental health conversation data, with a focus on:

- Efficient data storage (MySQL)
- Background processing (Celery + Redis)
- Vector database search (Milvus)
- LLM-based retrieval-augmented generation (OpenAI)

The scope of this PRD includes backend design and implementation details only. Frontend or UI design is out of scope.

## 2. Project Overview

### Purpose

- Provide mental health counselors with a tool to query conversation data, analyze sentiment, and receive generation-assisted suggestions for patient care
- Ensure an extensible and scalable design so new features can be added easily

### Core Technologies

- Python (primary language)
- FastAPI (for REST APIs)
- Celery + Redis (background jobs & queue)
- MySQL (primary relational DB)
- Milvus (vector DB for embeddings)
- SQLAlchemy (ORM)
- Alembic (DB migrations)
- DotEnv (environment variables)
- Pydantic (models & validation)
- OpenAI (generation & embeddings)
- Poetry (dependency management)

## 3. Detailed Functional Requirements

### 3.0 Poetry Setup
Setup poetry in the project root. Use python 3.11.11. Install the dependencies. Install black and isort. Poetry package name is `app`.

### 3.1 Database Setup and CRUD APIs

#### MySQL DB Setup & Migrations

- Use Alembic for migrations and tracking schema changes
- Database name: `legacy_development` (configure in `.env`)
- There is only one table in the project. Table: `mental_health_conversations`
  - `id`: unique PK (integer)
  - `created_at`: datetime (auto-updates on insert)
  - `updated_at`: datetime (auto-updates on update)
  - `question`: string
  - `answer`: string
  - `question_sentiment`: enum (positive, negative, neutral)
  - `answer_sentiment`: enum (positive, negative, neutral)

#### CRUD APIs

- Endpoint Prefix: `/api/v1/conversations`
- Methods: Create, Read (list and detail), Update, Delete
- Framework: FastAPI
- Data Access: Use SQLAlchemy ORM for reading/writing

#### API Client

- Provide a Python API Client for external services or scripts to interact with the conversation data without directly calling the DB
- Use Pydantic models for typed request and response models

### 3.2 Data Ingestion

#### Dataset Format

- Input: CSV with 4 fields (question, answer, question_sentiment, answer_sentiment)
- Goal: Import CSV data into the `mental_health_conversations` table

#### Data Import Script

- A standalone script (e.g., `data_import.py`) that:
  - Reads CSV from local filesystem
  - Uses the API Client (not ORM directly) to create records in MySQL

#### Vector Database Indexing via Celery

- Milvus Setup: Collection name `mental_health_embeddings_development`
  - Stores:
    - id (MySQL record PK)
    - embedding
    - question
    - question_sentiment
- Celery Workers:
  - `CreatedMentalHealthConversationJob`: Insert into Milvus after a new record is created in MySQL
  - `UpdatedMentalHealthConversationJob`: Update corresponding record in Milvus
  - `DeletedMentalHealthConversationJob`: Remove corresponding record from Milvus
- REST API Integration: After each CRUD operation commits to the MySQL DB, enqueue the corresponding Celery job to sync with Milvus

### 3.3 RAG Search and Generation

#### OpenAI & RAG Generation Service

Users can enter free-text queries describing a challenge with a patient.
The system:
- Searches Milvus for top 3 hits by similarity
- Retrieves question and answer fields for those top 3 hits
- Renders a Jinja prompt (startup prompt in `startup_prompt.jinja`)
- Calls OpenAI with the compiled prompt
- Returns the LLM-generated result

#### RAG Search API Endpoint

- Endpoint: (e.g.) POST `/api/v1/rag_search`
- Request: JSON body with user's question text
- Response: The generated text from OpenAI, incorporating the retrieved Q/A context from Milvus

## 4. Reference Documentation & Example Code

### 4.1 Milvus + OpenAI Example

Below is an example demonstrating how you might integrate Milvus and OpenAI. This snippet is illustrative—not production-ready. It shows how to create a Milvus collection, generate embeddings via OpenAI, and perform a search.

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

Key Takeaways:
- Creating a Milvus collection (with a vector field)
- Generating OpenAI embeddings
- Inserting records, searching, and deleting records

## 5. Recommended Project Structure

Below is an example structure to keep the project modular and maintainable. Folders and files can be adapted as needed:

```
project-root/
├── README.md
├── pyproject.toml
├── poetry.lock
├── .env              # Environment variables for DB, Redis, OpenAI, etc.
├── .env.local        # Local overrides, typically .gitignore'd
├── docker-compose.yml
├── my_milvus.db      # Milvus local file (if using local Milvus deployment)
├── train.csv         # The CSV dataset
│
├── app/
│   ├── __init__.py
│   ├── main.py       # FastAPI entrypoint (Uvicorn runs this)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── controllers.py   # CRUD endpoints
│   │       ├── routes.py        # Router (include_router) for /api/v1
│   │       └── schemas.py       # Pydantic request/response models
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py           # SQLAlchemy session creation
│   │   ├── base.py              # Base metadata for SQLAlchemy
│   │   └── migrations/          # Alembic migrations
│   │       ├── env.py
│   │       ├── script.py.mako
│   │       └── versions/        # Auto-generated migration files
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── mental_health_conversation.py  # SQLAlchemy model
│   │
│   ├── workers/                 # Celery workers & tasks
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   └── tasks.py
│   │
│   ├── services/                # Business logic / specialized services
│   │   ├── __init__.py
│   │   └── rag_generation.py    # RAG logic with Milvus + OpenAI
│   │
│   ├── clients/
│   │   ├── __init__.py
│   │   └── mental_health_conversations_client.py
│   │       # Python API client + Pydantic models
│   │
│   ├── templates/
│   │   └── startup_prompt.jinja # Jinja template for prompt construction
│   │
│   └── config.py                # Centralized config logic if needed
│
├── scripts/
│   └── data_import.py           # CSV ingestion script
│
└── tests/
    ├── __init__.py
    └── test_api.py
```

### Notes on Key Folders

- `app/api/v1`: Contains FastAPI controllers, routes, and Pydantic schemas for versioned API endpoints
- `app/db/migrations`: Alembic migration files and configuration
- `app/workers`: Contains Celery app initialization and the tasks that interact with Milvus
- `app/services`: Contains "business logic," such as RAG generation steps
- `app/clients`: A Python client for your own service or any external service. Use Pydantic for typed results
- `scripts/`: One-off or utility scripts (e.g., data import)
- `tests/`: Automated tests (e.g., Pytest)

## 6. Development & Deployment Flow

### Setup

Install dependencies:
```bash
poetry install
```

Configure environment variables in `.env`.

### Database Migrations

Use Alembic to manage schema changes:
```bash
alembic revision --autogenerate -m "Create mental_health_conversations table"
alembic upgrade head
```

### Running the Project

Start the required services (MySQL, Redis, Milvus) via Docker Compose:
```bash
docker-compose up -d
```

Start FastAPI (e.g., with Uvicorn):
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Run Celery workers:
```bash
celery -A app.workers.celery_app worker --loglevel=info
```

### Data Ingestion

Run the CSV import script (using the internal API client):
```bash
python scripts/data_import.py
```

### RAG Endpoints

Test RAG flows at `/api/v1/rag_search` (POST), or wherever it is registered.

### Testing

Implement unit tests in `tests/` and run them:
```bash
pytest
```

## 7. Success Criteria & Acceptance

- Data Access: Counselors can query mental health conversations, filter by sentiment, and retrieve relevant answers
- Background Sync: Any CRUD operation automatically syncs to Milvus via Celery tasks
- RAG: Users can provide a free-text question, retrieve top 3 relevant results from Milvus, and receive a generated answer from OpenAI
- Scalability: Project structure supports future expansions (new models, new microservices, further Celery tasks, etc.)

### Important Notes

- The example Milvus code above is only to illustrate the typical usage pattern; actual integration logic will reside in `rag_generation.py` or Celery tasks
- The file structure is a recommendation that follows typical Python best practices and might be tweaked to fit your team's conventions
- Always ensure API keys, database credentials, and other sensitive information are stored in environment variables and excluded from version control