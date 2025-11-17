"""Configuration settings optimized for high-traffic scenarios."""
import os
from datetime import timedelta


def get_database_url():
    """Get database URL, converting postgres:// to postgresql:// for SQLAlchemy compatibility."""
    database_url = os.environ.get('DATABASE_URL') or 'sqlite:///signup.db'
    # Heroku uses postgres:// but SQLAlchemy needs postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    return database_url


class Config:
    """Base configuration with performance optimizations."""
    
    # Flask Core
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration with Connection Pooling
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = False  # Disable for performance
    
    # PostgreSQL Connection Pool Settings (for high traffic)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DATABASE_POOL_SIZE', 20)),
        'max_overflow': int(os.environ.get('DATABASE_MAX_OVERFLOW', 30)),
        'pool_timeout': int(os.environ.get('DATABASE_POOL_TIMEOUT', 30)),
        'pool_recycle': 3600,  # Recycle connections every hour
        'pool_pre_ping': True,  # Verify connections before use
    }
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Flask-Caching for performance
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'redis')
    CACHE_REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes default cache
    
    # Rate Limiting Configuration
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL') or 'redis://localhost:6379/1'
    REQUESTS_PER_MINUTE = int(os.environ.get('REQUESTS_PER_MINUTE', 10))
    REQUESTS_PER_HOUR = int(os.environ.get('REQUESTS_PER_HOUR', 100))
    
    # Celery Configuration for Async Processing
    # Use REDIS_URL if CELERY_BROKER_URL not set (Heroku provides REDIS_URL)
    redis_url = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or redis_url
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or redis_url
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    
    # SMS Configuration
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER')
    
    # Form Configuration (cacheable)
    FORM_TITLE = os.environ.get('FORM_TITLE', 'Kansas City FIFA Fan Fest Signup')
    DEFAULT_EVENTS = os.environ.get('DEFAULT_EVENTS', 
                                  'World Cup Viewing,Skills Challenge,Photo Booth,Food Trucks,Live Music')
    
    # Performance Settings
    WTF_CSRF_TIME_LIMIT = 1800  # CSRF token timeout in seconds (30 minutes)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Production Settings
    FORCE_HTTPS = os.environ.get('FORCE_HTTPS', 'false').lower() == 'true'
    CDN_URL = os.environ.get('CDN_URL', '')
    
    # Monitoring
    METRICS_ENABLED = os.environ.get('METRICS_ENABLED', 'true').lower() == 'true'
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    
    # Admin Configuration
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'  # Change in production!
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration with additional optimizations."""
    DEBUG = False
    TESTING = False
    
    # Additional production optimizations
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'pool_size': 50,  # Larger pool for production
        'max_overflow': 100,
    }
    
    # Longer cache times in production
    CACHE_DEFAULT_TIMEOUT = 1800  # 30 minutes


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    CACHE_TYPE = 'simple'  # In-memory cache for tests
    CELERY_TASK_ALWAYS_EAGER = True  # Synchronous tasks in tests


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

