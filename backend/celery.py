from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.beat_schedule = {
    'check-sessions-and-notify': {
        'task': 'core.tasks.session_notifier',
        'schedule': 60
    },
    'check-active-chats': {
        'task': 'core.tasks.chat_checker',
        'schedule': 300
    },
    'check-end-sessions': {
        'task': 'core.tasks.check_end_session',
        'schedule': 300
    },
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()




@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
