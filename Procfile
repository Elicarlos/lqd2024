web: gunicorn liquida2018.wsgi --log-file -
worker: celery -A liquida2018 worker --loglevel=info
flower: celery -A your_project_name flower --port=5555 --basic_auth=${FLOWER_USERNAME}:${FLOWER_PASSWORD}
