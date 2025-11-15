"""Test form validation."""
import pytest
from app import SignupForm, create_app


@pytest.fixture
def app_context():
    """Create app context for form testing."""
    app = create_app('testing')
    with app.app_context():
        with app.test_request_context():
            yield app


def test_valid_signup_form(app_context):
    """Test valid form submission."""
    form = SignupForm(
        name='John Doe',
        email='john.doe@example.com',
        phone='5551234567',
        zip_code='64111',
        events_interested=['Event 1', 'Event 2']
    )
    
    # Note: In testing, CSRF is disabled
    assert form.validate() is True


def test_form_missing_name(app_context):
    """Test form validation with missing name."""
    form = SignupForm(
        name='',
        email='john.doe@example.com',
        zip_code='64111',
        events_interested=['Event 1']
    )
    
    assert form.validate() is False
    assert 'name' in form.errors


def test_form_missing_email(app_context):
    """Test form validation with missing email."""
    form = SignupForm(
        name='John Doe',
        email='',
        zip_code='64111',
        events_interested=['Event 1']
    )
    
    assert form.validate() is False
    assert 'email' in form.errors


def test_form_invalid_email_format(app_context):
    """Test form validation with invalid email format."""
    form = SignupForm(
        name='John Doe',
        email='not-an-email',
        zip_code='64111',
        events_interested=['Event 1']
    )
    
    assert form.validate() is False
    assert 'email' in form.errors


def test_form_missing_zip_code(app_context):
    """Test form validation with missing zip code."""
    form = SignupForm(
        name='John Doe',
        email='john.doe@example.com',
        zip_code='',
        events_interested=['Event 1']
    )
    
    assert form.validate() is False
    assert 'zip_code' in form.errors


def test_form_invalid_zip_code_too_short(app_context):
    """Test form validation with zip code too short."""
    form = SignupForm(
        name='John Doe',
        email='john.doe@example.com',
        zip_code='123',
        events_interested=['Event 1']
    )
    
    assert form.validate() is False
    assert 'zip_code' in form.errors


def test_form_missing_events(app_context):
    """Test form validation with no events selected."""
    form = SignupForm(
        name='John Doe',
        email='john.doe@example.com',
        zip_code='64111',
        events_interested=[]
    )
    
    assert form.validate() is False
    assert 'events_interested' in form.errors


def test_form_phone_optional(app_context):
    """Test that phone number is optional."""
    form = SignupForm(
        name='John Doe',
        email='john.doe@example.com',
        phone='',
        zip_code='64111',
        events_interested=['Event 1']
    )
    
    assert form.validate() is True


def test_form_name_too_long(app_context):
    """Test form validation with name exceeding max length."""
    form = SignupForm(
        name='A' * 101,  # Exceeds 100 character limit
        email='john.doe@example.com',
        zip_code='64111',
        events_interested=['Event 1']
    )
    
    assert form.validate() is False
    assert 'name' in form.errors


def test_form_name_too_short(app_context):
    """Test form validation with name too short."""
    form = SignupForm(
        name='A',  # Less than 2 characters
        email='john.doe@example.com',
        zip_code='64111',
        events_interested=['Event 1']
    )
    
    assert form.validate() is False
    assert 'name' in form.errors


def test_form_email_too_long(app_context):
    """Test form validation with email exceeding max length."""
    form = SignupForm(
        name='John Doe',
        email='a' * 110 + '@example.com',  # Exceeds 120 character limit
        zip_code='64111',
        events_interested=['Event 1']
    )
    
    assert form.validate() is False
    assert 'email' in form.errors

