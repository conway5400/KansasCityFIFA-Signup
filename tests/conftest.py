"""Pytest configuration and fixtures for testing."""
import os
import pytest
from app import create_app, db
from config import TestingConfig


@pytest.fixture(scope='session')
def app():
    """Create application instance for testing."""
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client for making requests."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create CLI runner for testing CLI commands."""
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def clean_db(app):
    """Clean database before each test."""
    with app.app_context():
        # Clear all tables before each test
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()


@pytest.fixture
def sample_signup_data():
    """Sample signup data for testing."""
    return {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '5551234567',
        'zip_code': '64111',
        'events_interested': ['World Cup Viewing Parties', 'Skills Challenge & Games']
    }


@pytest.fixture
def sample_signup_form_data(sample_signup_data):
    """Sample form data for testing (includes CSRF token)."""
    data = sample_signup_data.copy()
    data['csrf_token'] = 'test_token'  # WTF_CSRF_ENABLED is False in testing
    return data

