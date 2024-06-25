from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Define o módulo de configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liquida2018.settings')

app = Celery('liquida2018')

# Lê as configurações do Django e namespace 'CELERY'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre e carrega tarefas automaticamente dos módulos tasks.py
app.autodiscover_tasks()
