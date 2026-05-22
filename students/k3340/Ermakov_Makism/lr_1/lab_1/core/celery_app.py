import os

from celery import Celery


celery_app = Celery(
    "time_manager_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
)

celery_app.conf.update(
    accept_content=["json"],
    enable_utc=True,
    imports=("core.parser_tasks",),
    result_expires=3600,
    result_serializer="json",
    task_serializer="json",
    task_track_started=True,
    timezone="UTC",
)
