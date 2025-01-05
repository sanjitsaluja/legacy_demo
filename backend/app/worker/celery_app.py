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
