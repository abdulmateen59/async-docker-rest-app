from celery import Celery

from settings import Settings

settings = Settings()


def make_celery():
    return Celery(
        'worker',
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=["celery_app.tasks"],
        task_track_started=True,
    )


celery_app = make_celery()
celery_app.autodiscover_tasks()
celery_app.conf.beat_schedule = {
    'send-emails-periodically': {
        'task': 'celery_app.tasks.send_email',
        'schedule': 60,  # every minute
    },
}
celery_app.conf.timezone = 'UTC'

# sentry_sdk.init(
#     dsn='',
#     integrations=[
#         CeleryIntegration(),
#     ],
#     traces_sample_rate=1.0,
# )
