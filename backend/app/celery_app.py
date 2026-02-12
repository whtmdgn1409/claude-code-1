"""
Celery application configuration for background tasks.
Handles periodic crawling and notification scheduling.
"""
from celery import Celery
from celery.schedules import crontab

from app.config import settings


# Create Celery app
celery_app = Celery(
    "dealmoa",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.crawler",
        "app.tasks.notification"
    ]
)

# Configure Celery
celery_app.conf.update(
    timezone=settings.CELERY_TIMEZONE,
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    task_track_started=settings.CELERY_TASK_TRACK_STARTED,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    result_expires=3600,  # Results expire after 1 hour
    worker_prefetch_multiplier=1,  # Prefetch one task at a time
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks (prevent memory leaks)
)

# Configure Celery Beat schedule
celery_app.conf.beat_schedule = {
    # Crawl Ppomppu every 5 minutes
    "crawl-ppomppu-every-5-minutes": {
        "task": "app.tasks.crawler.run_ppomppu_crawler",
        "schedule": 300.0,  # 5 minutes in seconds
        "options": {
            "expires": 240  # Task expires if not executed within 4 minutes
        }
    },
    # Send scheduled notifications every 10 minutes
    "send-scheduled-notifications-every-10-minutes": {
        "task": "app.tasks.notification.send_scheduled_notifications",
        "schedule": crontab(minute="*/10"),  # Every 10 minutes
        "options": {
            "expires": 540  # Task expires after 9 minutes
        }
    },
}

# Configure task routes (optional, for future use)
celery_app.conf.task_routes = {
    "app.tasks.crawler.*": {"queue": "crawler"},
    "app.tasks.notification.*": {"queue": "notification"},
}
