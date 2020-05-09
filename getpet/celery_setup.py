import os

import celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'getpet.settings')

app = celery.Celery('getpet')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
