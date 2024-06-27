web: gunicorn liquida2018.wsgi --log-file -
work: celery -A liquida2018 work --loglevel=info
flower: celery -A your_project_name flower --port=5555 --basic_auth=${FLOWER_USERNAME}:${FLOWER_PASSWORD}
