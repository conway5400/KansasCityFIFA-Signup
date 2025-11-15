web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --worker-class gthread --threads 2 --timeout 120 --keep-alive 5 --access-logfile - --error-logfile - "app:create_app()"
worker: celery -A app.celery worker --loglevel=info --concurrency=4 --max-tasks-per-child=1000
release: flask db upgrade

