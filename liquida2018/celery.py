from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from decouple import config
import ssl
# Define the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liquida2018.settings')

app = Celery('liquida2018')

# Obtain the Redis URL
redis_url = config('REDIS_URL', '')

# Append SSL cert requirement if using rediss
if redis_url.startswith('rediss://'):
    redis_url += '?ssl_cert_reqs=CERT_NONE'

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(
    broker_url=redis_url,
    result_backend=redis_url,
    redis_max_connections=20,
    worker_max_tasks_per_child=10,
    task_soft_time_limit=3600,  # 1 hour
    task_time_limit=3660,       # 1 hour and 1 minute
    broker_connection_retry_on_startup=True,
    broker_transport_options={
        'visibility_timeout': 43200,  # 12 hours
        'fanout_prefix': True,
        'fanout_patterns': True,
    },
    worker_concurrency=4,
    redis_backend_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE},  # Adicione esta linha para o backend Redis
    broker_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE},         # Adicione e# Adjust based on available resources
)



# Configure Celery to use JSON as the serialization format
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

# Configure Celery to use UTC
app.conf.enable_utc = True

# Configure the timezone for Celery (adjust as necessary)
app.conf.timezone = 'America/Sao_Paulo'

# Autodiscover tasks in tasks.py
app.autodiscover_tasks()
