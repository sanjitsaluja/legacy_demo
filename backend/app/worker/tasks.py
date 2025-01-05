from app.worker.celery_app import celery_app


@celery_app.task(name="app.worker.tasks.index_conversation")
def index_conversation(conversation_id: int):
    """
    Index a conversation in the vector database.
    For now, this is just a placeholder that logs the conversation ID.
    """
    print(f"Indexing conversation {conversation_id}")
    # TODO: Add vector database indexing logic
    return True
