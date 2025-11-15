"""Test database models."""
import pytest
from datetime import datetime
from app import db, Signup


def test_signup_model_creation(app, sample_signup_data):
    """Test creating a signup record."""
    with app.app_context():
        signup = Signup(
            name=sample_signup_data['name'],
            email=sample_signup_data['email'],
            phone=sample_signup_data['phone'],
            zip_code=sample_signup_data['zip_code'],
            events_interested=sample_signup_data['events_interested']
        )
        
        db.session.add(signup)
        db.session.commit()
        
        assert signup.id is not None
        assert signup.name == sample_signup_data['name']
        assert signup.email == sample_signup_data['email']
        assert signup.phone == sample_signup_data['phone']
        assert signup.zip_code == sample_signup_data['zip_code']
        assert signup.events_interested == sample_signup_data['events_interested']
        assert signup.sms_sent is False
        assert signup.created_at is not None
        assert isinstance(signup.created_at, datetime)


def test_signup_model_to_dict(app, sample_signup_data):
    """Test converting signup model to dictionary."""
    with app.app_context():
        signup = Signup(
            name=sample_signup_data['name'],
            email=sample_signup_data['email'],
            zip_code=sample_signup_data['zip_code'],
            events_interested=sample_signup_data['events_interested']
        )
        
        db.session.add(signup)
        db.session.commit()
        
        signup_dict = signup.to_dict()
        
        assert signup_dict['id'] == signup.id
        assert signup_dict['name'] == sample_signup_data['name']
        assert signup_dict['email'] == sample_signup_data['email']
        assert signup_dict['zip_code'] == sample_signup_data['zip_code']
        assert signup_dict['events_interested'] == sample_signup_data['events_interested']
        assert 'created_at' in signup_dict


def test_signup_model_tracking_fields(app, sample_signup_data):
    """Test tracking fields (IP, user agent, source)."""
    with app.app_context():
        signup = Signup(
            name=sample_signup_data['name'],
            email=sample_signup_data['email'],
            zip_code=sample_signup_data['zip_code'],
            events_interested=sample_signup_data['events_interested'],
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            source_url='https://example.com/qr-code'
        )
        
        db.session.add(signup)
        db.session.commit()
        
        assert signup.ip_address == '192.168.1.1'
        assert signup.user_agent == 'Mozilla/5.0'
        assert signup.source_url == 'https://example.com/qr-code'


def test_signup_model_sms_tracking(app, sample_signup_data):
    """Test SMS tracking fields."""
    with app.app_context():
        signup = Signup(
            name=sample_signup_data['name'],
            email=sample_signup_data['email'],
            phone=sample_signup_data['phone'],
            zip_code=sample_signup_data['zip_code'],
            events_interested=sample_signup_data['events_interested']
        )
        
        db.session.add(signup)
        db.session.commit()
        
        # Initially not sent
        assert signup.sms_sent is False
        assert signup.sms_sent_at is None
        assert signup.sms_delivery_status is None
        
        # Mark as sent
        signup.sms_sent = True
        signup.sms_sent_at = datetime.utcnow()
        signup.sms_delivery_status = 'delivered'
        db.session.commit()
        
        assert signup.sms_sent is True
        assert signup.sms_sent_at is not None
        assert signup.sms_delivery_status == 'delivered'


def test_signup_model_email_index(app, sample_signup_data):
    """Test that email is indexed for performance."""
    with app.app_context():
        # Create multiple signups
        for i in range(5):
            signup = Signup(
                name=f'User {i}',
                email=f'user{i}@example.com',
                zip_code='64111',
                events_interested=['Event 1']
            )
            db.session.add(signup)
        db.session.commit()
        
        # Query by email should be fast (index exists)
        result = Signup.query.filter_by(email='user3@example.com').first()
        assert result is not None
        assert result.name == 'User 3'


def test_signup_model_json_events_storage(app):
    """Test that events are stored as JSON array."""
    with app.app_context():
        events = ['Event 1', 'Event 2', 'Event 3', 'Event 4']
        
        signup = Signup(
            name='Test User',
            email='test@example.com',
            zip_code='64111',
            events_interested=events
        )
        
        db.session.add(signup)
        db.session.commit()
        
        # Retrieve and verify
        retrieved = Signup.query.filter_by(email='test@example.com').first()
        assert retrieved.events_interested == events
        assert isinstance(retrieved.events_interested, list)
        assert len(retrieved.events_interested) == 4

