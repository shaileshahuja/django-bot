from __future__ import absolute_import

import os

from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example.settings')

app = Celery('example')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update_user_list': {
        'task': 'converse.tasks.update_user_list',
        'schedule': crontab(hour=3, minute=30)
    },
}
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600
)
