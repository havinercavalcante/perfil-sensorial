import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'perfil_sensorial.settings')

app = Celery('perfil_sensorial')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
