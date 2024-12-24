from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryManagement.settings')

app = Celery('LibraryManagement')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in the `tasks.py` file of each app
app.autodiscover_tasks()
