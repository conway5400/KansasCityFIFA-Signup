"""Celery application entry point for worker."""
from app import create_app

flask_app = create_app()
celery = flask_app.celery

