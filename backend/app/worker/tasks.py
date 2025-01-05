import asyncio

from celery.utils.log import get_task_logger

from app.client.api_client import APIClient
from app.db.milvus_client import milvus_client
from app.utils.embeddings import get_combined_embedding
from app.worker.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name="app.worker.tasks.index_conversation", bind=True)
def index_conversation(self, conversation_id: int):
    """Index a conversation in the vector database."""
    logger.info(f"Task ID: {self.request.id}")
    logger.info(f"Starting to index conversation {conversation_id}")

    async def _index():
        async with APIClient() as client:
            try:
                logger.info("Attempting to get conversation from API")
                conversation = await client.get_conversation(conversation_id)
                if not conversation:
                    logger.error(f"Conversation {conversation_id} not found")
                    return False

                logger.info("Generating embedding")
                embedding = get_combined_embedding(
                    question=conversation.question, answer=conversation.answer
                )

                logger.info("Preparing data for Milvus")
                data = [
                    {
                        "id": conversation_id,
                        "question": conversation.question,
                        "answer": conversation.answer,
                        "embedding": embedding,
                    }
                ]

                logger.info("Attempting to insert into Milvus")
                result = milvus_client.insert(
                    collection_name="mental_health_conversations", data=data
                )
                logger.info(f"Milvus insert result: {result}")

                return True

            except Exception as e:
                logger.exception(f"Error indexing conversation {conversation_id}")
                return False

    try:
        return asyncio.run(_index())
    except Exception as e:
        logger.exception("Error in task execution")
        return False


@celery_app.task(name="app.worker.tasks.delete_conversation_index")
def delete_conversation_index(conversation_id: int):
    """Delete a conversation from the vector database."""
    logger.info(f"Deleting conversation {conversation_id} from vector index")

    try:
        # Delete from Milvus
        result = milvus_client.delete(
            collection_name="mental_health_conversations", pks=[conversation_id]
        )
        logger.info(f"Deleted conversation {conversation_id} from Milvus")
        return True

    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {e}")
        return False
