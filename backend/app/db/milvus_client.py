import os
from pathlib import Path

from dotenv import load_dotenv
from pymilvus import DataType, MilvusClient

# Load environment variables
load_dotenv(".env.local")

# Get project root directory
ROOT_DIR = Path(__file__).parent.parent.parent

# Milvus configuration
COLLECTION_NAME = "mental_health_conversations"
EMBEDDING_DIM = 1536  # OpenAI ada-002 dimension

# Initialize Milvus client
milvus_client = MilvusClient(uri=os.getenv("MILVUS_URI"))


def init_milvus():
    """Initialize Milvus collection if it doesn't exist."""
    if not milvus_client.has_collection(COLLECTION_NAME):
        print(f"Creating collection {COLLECTION_NAME}...")

        # Create schema
        schema = milvus_client.create_schema(
            auto_id=False,
            enable_dynamic_field=True,
        )

        # Add fields to schema
        schema.add_field(
            field_name="id",
            datatype=DataType.INT64,
            is_primary=True,
            description="conversation id",
        )
        schema.add_field(
            field_name="question",
            datatype=DataType.VARCHAR,
            max_length=65535,
            description="conversation question",
        )
        schema.add_field(
            field_name="answer",
            datatype=DataType.VARCHAR,
            max_length=65535,
            description="conversation answer",
        )
        schema.add_field(
            field_name="embedding",
            datatype=DataType.FLOAT_VECTOR,
            dim=EMBEDDING_DIM,
            description="combined question-answer embedding",
        )

        # Prepare index parameters
        index_params = milvus_client.prepare_index_params()
        index_params.add_index(
            field_name="embedding",
            index_type="IVF_FLAT",
            metric_type="COSINE",
            params={"nlist": 1024},
        )

        # Create collection with schema and index
        milvus_client.create_collection(
            collection_name=COLLECTION_NAME,
            schema=schema,
            index_params=index_params,
        )

        print(f"Created collection and index for {COLLECTION_NAME}")
    else:
        print(f"Collection {COLLECTION_NAME} already exists")


def reset_milvus():
    """Drop and recreate the Milvus collection."""
    if milvus_client.has_collection(COLLECTION_NAME):
        print(f"Dropping collection {COLLECTION_NAME}...")
        milvus_client.drop_collection(COLLECTION_NAME)
    init_milvus()


if __name__ == "__main__":
    # Create data directory if it doesn't exist
    data_dir = ROOT_DIR / "data"
    data_dir.mkdir(exist_ok=True)

    # Initialize Milvus
    reset_milvus()
