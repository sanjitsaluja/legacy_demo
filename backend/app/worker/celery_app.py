import logging
import os

from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")

# Initialize Celery
celery_app = Celery(
    "worker",
    broker=f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/0",
    backend=f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/0",
    include=["app.worker.tasks"],
)

# Optional configurations
celery_app.conf.task_routes = {"app.worker.tasks.*": {"queue": "main-queue"}}

# Configure logging
celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    worker_redirect_stdouts=True,
    worker_log_color=True,
    task_send_sent_event=True,
    worker_send_task_events=True,
)

# Add this logging configuration
logging.basicConfig(level=logging.DEBUG)
