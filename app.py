"""
Kansas City FIFA Signup - Scalable Flask Application
Designed for high-traffic loads (hundreds of thousands of hits)
"""
import os
import logging
from datetime import datetime
from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from celery import Celery
import structlog
import redis
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from wtforms import StringField, TextAreaField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Email, Length
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


def create_app(config_name=None):
    """Create Flask application with optimized configuration."""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize Sentry for error tracking
    if app.config.get('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[
                FlaskIntegration(),
                CeleryIntegration(),
            ],
            traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
            profiles_sample_rate=0.1,  # 10% for profiling
            environment=config_name,
            release=os.environ.get('HEROKU_SLUG_COMMIT', 'development'),
        )
        logger.info("sentry_initialized", environment=config_name)
    
    # Configure logging
    logging.basicConfig(level=app.config['LOG_LEVEL'])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    limiter.init_app(app)
    
    # Configure Celery and attach to app for worker access
    celery = make_celery(app)
    app.celery = celery  # Make accessible via app.celery
    
    # Register routes
    register_routes(app, celery)
    
    # Register CLI commands
    register_commands(app)
    
    return app


def make_celery(app):
    """Create Celery instance for async processing."""
    # Handle SSL Redis URLs (rediss://) for Heroku
    # Celery requires ssl_cert_reqs parameter for SSL Redis connections
    def add_ssl_cert_reqs(url):
        """Add ssl_cert_reqs parameter to rediss:// URLs if not present."""
        if url and url.startswith('rediss://'):
            if 'ssl_cert_reqs' not in url:
                separator = '&' if '?' in url else '?'
                url = url + separator + 'ssl_cert_reqs=CERT_NONE'
        return url
    
    # Update config with SSL parameters before creating Celery
    broker_url = app.config['CELERY_BROKER_URL']
    result_backend = app.config['CELERY_RESULT_BACKEND']
    
    broker_url = add_ssl_cert_reqs(broker_url)
    result_backend = add_ssl_cert_reqs(result_backend)
    
    # Update config dict so Celery reads the modified URLs
    app.config['CELERY_BROKER_URL'] = broker_url
    app.config['CELERY_RESULT_BACKEND'] = result_backend
    
    celery = Celery(
        app.import_name,
        backend=result_backend,
        broker=broker_url
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery


# Database Models (Optimized for Performance)
class Signup(db.Model):
    """Optimized signup model for high-traffic scenarios."""
    __tablename__ = 'signups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True, index=True)  # For SMS
    zip_code = db.Column(db.String(10), nullable=False, index=True)
    events_interested = db.Column(db.JSON, nullable=False)  # Array of event names
    
    # Tracking fields
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    user_agent = db.Column(db.String(500), nullable=True)
    source_url = db.Column(db.String(200), nullable=True)  # QR code tracking
    
    # SMS tracking
    sms_sent = db.Column(db.Boolean, default=False, nullable=False)
    sms_sent_at = db.Column(db.DateTime, nullable=True)
    sms_delivery_status = db.Column(db.String(20), nullable=True)  # delivered, failed, etc.
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Database indexes for performance
    __table_args__ = (
        db.Index('ix_signups_created_date', 'created_at'),
        db.Index('ix_signups_email_created', 'email', 'created_at'),
        db.Index('ix_signups_zip_created', 'zip_code', 'created_at'),
    )
    
    def __repr__(self):
        return f'<Signup {self.email}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON responses."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'zip_code': self.zip_code,
            'events_interested': self.events_interested,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Forms with Validation
class MultiCheckboxField(SelectMultipleField):
    """Custom field for multiple checkboxes."""
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class SignupForm(FlaskForm):
    """Optimized signup form with validation."""
    name = StringField('Full Name', validators=[
        DataRequired(message="Name is required"),
        Length(min=2, max=100, message="Name must be between 2 and 100 characters")
    ])
    
    email = StringField('Email Address', validators=[
        DataRequired(message="Email is required"),
        Email(message="Please enter a valid email address"),
        Length(max=120, message="Email is too long")
    ])
    
    phone = StringField('Phone Number (Optional)', validators=[
        Length(max=20, message="Phone number is too long")
    ])
    
    zip_code = StringField('Zip Code', validators=[
        DataRequired(message="Zip code is required"),
        Length(min=5, max=10, message="Please enter a valid zip code")
    ])
    
    events_interested = MultiCheckboxField('Events You\'re Interested In', 
                                         validators=[DataRequired(message="Please select at least one event")])


def register_routes(app, celery):
    """Register all application routes."""
    
    @app.route('/')
    @limiter.limit("20 per minute")
    @cache.cached(timeout=300, key_prefix='form_config')
    def index():
        """Display signup form with cached configuration."""
        try:
            form = SignupForm()
            
            # Load event options (cached)
            events = get_event_options()
            form.events_interested.choices = [(event, event) for event in events]
            
            # Track page views
            logger.info("form_displayed", 
                       ip=request.remote_addr,
                       user_agent=request.headers.get('User-Agent', ''))
            
            return render_template('index.html', form=form)
            
        except Exception as e:
            logger.error("form_display_error", error=str(e))
            return render_template('error.html'), 500
    
    @app.route('/signup', methods=['POST'])
    @limiter.limit("5 per minute")  # Stricter limit for form submissions
    def signup():
        """Process signup form submission."""
        try:
            form = SignupForm()
            events = get_event_options()
            form.events_interested.choices = [(event, event) for event in events]
            
            if form.validate_on_submit():
                # Check for duplicate email (with cache)
                cache_key = f"email_check:{form.email.data}"
                if cache.get(cache_key):
                    logger.warning("duplicate_email_attempt", email=form.email.data)
                    return render_template('index.html', form=form, 
                                        error="This email has already been registered.")
                
                # Create signup record
                signup_data = Signup(
                    name=form.name.data.strip(),
                    email=form.email.data.strip().lower(),
                    phone=form.phone.data.strip() if form.phone.data else None,
                    zip_code=form.zip_code.data.strip(),
                    events_interested=form.events_interested.data,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', ''),
                    source_url=request.referrer
                )
                
                db.session.add(signup_data)
                db.session.commit()
                
                # Cache email to prevent duplicates
                cache.set(cache_key, True, timeout=3600)  # 1 hour
                
                # Send SMS asynchronously if phone provided
                if signup_data.phone:
                    send_sms_async.delay(signup_data.id, signup_data.phone, signup_data.name)
                
                logger.info("signup_completed", 
                           signup_id=signup_data.id,
                           email=signup_data.email,
                           events_count=len(signup_data.events_interested))
                
                return redirect(url_for('success', signup_id=signup_data.id))
            
            else:
                logger.warning("form_validation_failed", errors=form.errors)
                return render_template('index.html', form=form)
                
        except Exception as e:
            logger.error("signup_error", error=str(e))
            db.session.rollback()
            return render_template('error.html'), 500
    
    @app.route('/success/<int:signup_id>')
    @limiter.limit("10 per minute")
    def success(signup_id):
        """Display success page."""
        try:
            signup_data = Signup.query.get_or_404(signup_id)
            return render_template('success.html', signup=signup_data)
        except Exception as e:
            logger.error("success_page_error", error=str(e), signup_id=signup_id)
            return render_template('error.html'), 500
    
    @app.route('/health')
    def health():
        """Health check endpoint for load balancers."""
        try:
            # Quick database check
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})
        except Exception as e:
            logger.error("health_check_failed", error=str(e))
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 503
    
    @app.route('/metrics')
    def metrics():
        """Basic metrics endpoint."""
        if not app.config.get('METRICS_ENABLED'):
            return jsonify({'error': 'Metrics disabled'}), 404
            
        try:
            total_signups = Signup.query.count()
            recent_signups = Signup.query.filter(
                Signup.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).count()
            
            return jsonify({
                'total_signups': total_signups,
                'today_signups': recent_signups,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error("metrics_error", error=str(e))
            return jsonify({'error': 'Metrics unavailable'}), 500
    
    # Celery Tasks
    @celery.task(name='send_sms_async')
    def send_sms_async(signup_id, phone_number, name):
        """Send SMS confirmation asynchronously."""
        try:
            from services.sms_service import send_confirmation_sms
            
            result = send_confirmation_sms(phone_number, name)
            
            # Update signup record
            signup = Signup.query.get(signup_id)
            if signup:
                signup.sms_sent = True
                signup.sms_sent_at = datetime.utcnow()
                signup.sms_delivery_status = 'sent'
                db.session.commit()
            
            logger.info("sms_sent", signup_id=signup_id, phone=phone_number, result=result)
            return result
            
        except Exception as e:
            logger.error("sms_send_failed", signup_id=signup_id, error=str(e))
            
            # Update failure status
            signup = Signup.query.get(signup_id)
            if signup:
                signup.sms_delivery_status = 'failed'
                db.session.commit()
            
            raise


@cache.memoize(timeout=600)  # Cache for 10 minutes
def get_event_options():
    """Get event options (cached for performance)."""
    default_events = [
        "World Cup Viewing Parties",
        "Skills Challenge & Games", 
        "Photo Booth Experience",
        "Food Truck Festival",
        "Live Music & Entertainment",
        "Meet & Greet with Players",
        "FIFA Merchandise Shopping",
        "Kids Zone Activities"
    ]
    
    # In production, this could come from database or environment
    env_events = os.environ.get('DEFAULT_EVENTS', '').split(',')
    if env_events and env_events[0]:  # Check if not empty
        return [event.strip() for event in env_events]
    
    return default_events


def register_commands(app):
    """Register Flask CLI commands."""
    
    @app.cli.command()
    def init_db():
        """Initialize database with tables."""
        db.create_all()
        print("Database initialized!")
    
    @app.cli.command()
    def test_sms():
        """Test SMS sending functionality."""
        from services.sms_service import send_confirmation_sms
        
        phone = input("Enter phone number to test: ")
        name = input("Enter name: ")
        
        try:
            result = send_confirmation_sms(phone, name)
            print(f"SMS sent successfully: {result}")
        except Exception as e:
            print(f"SMS failed: {e}")


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
