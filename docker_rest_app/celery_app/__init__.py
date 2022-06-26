from celery import Celery
from celery.schedules import crontab

from settings import Settings

settings = Settings()


def make_celery():
    return Celery(
        'worker',
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        broker_transport_options={'visibility_timeout': 3600},
        result_backend_transport_options={'visibility_timeout': 3600},
        include=["celery_app.tasks"],
        task_track_started=True,
    )


celery_app = make_celery()
celery_app.autodiscover_tasks()
celery_app.conf.beat_schedule = {
    'send-emails-periodically': {
        'task': 'celery_app.tasks.send_email',
        'schedule': crontab(hour=1, minute=0),
    },
}
celery_app.conf.timezone = 'UTC'
