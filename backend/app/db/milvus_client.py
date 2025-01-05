import os
from pathlib import Path

from dotenv import load_dotenv
from pymilvus import CollectionSchema, DataType, FieldSchema, MilvusClient

# Load environment variables
load_dotenv(".env.local")

# Get project root directory
ROOT_DIR = Path(__file__).parent.parent.parent

# Milvus configuration
COLLECTION_NAME = "mental_health_conversations"
EMBEDDING_DIM = 1536  # OpenAI ada-002 dimension

# Initialize Milvus client
milvus_client = MilvusClient(
    uri=os.getenv("MILVUS_URI", str(ROOT_DIR / "data/milvus.db"))
)


def init_milvus():
    """Initialize Milvus collection if it doesn't exist."""
    if not milvus_client.has_collection(COLLECTION_NAME):
        print(f"Creating collection {COLLECTION_NAME}...")

        # Define fields for the collection
        fields = [
            {
                "name": "id",
                "dtype": DataType.INT64,
                "is_primary": True,
                "auto_id": False,
            },
            {"name": "question", "dtype": DataType.VARCHAR, "max_length": 65535},
            {"name": "answer", "dtype": DataType.VARCHAR, "max_length": 65535},
            {"name": "embedding", "dtype": DataType.FLOAT_VECTOR, "dim": EMBEDDING_DIM},
        ]

        # Create collection
        milvus_client.create_collection(collection_name=COLLECTION_NAME, fields=fields)

        # Create index
        milvus_client.create_index(
            collection_name=COLLECTION_NAME,
            field_name="embedding",
            index_params={
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024},
            },
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
    init_milvus()
