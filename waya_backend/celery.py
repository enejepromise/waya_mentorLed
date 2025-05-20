import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'waya_backend.settings')

app = Celery('waya_backend')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Example: Send a dummy reminder every minute
    'send-daily-reminder': {
        'task': 'users.tasks.send_dummy_reminder',
        'schedule': crontab(minute='*/1'),  # Every 1 minute (for testing)
    },
}
