import os

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(".env.local")

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_embedding(text: str) -> list:
    """Get OpenAI embedding for text."""
    response = openai_client.embeddings.create(
        input=text, model="text-embedding-ada-002"
    )
    return response.data[0].embedding


def get_combined_embedding(question: str, answer: str) -> list:
    """Get embedding for combined question and answer."""
    combined_text = f"Question: {question}\nAnswer: {answer}"
    return get_embedding(combined_text)
