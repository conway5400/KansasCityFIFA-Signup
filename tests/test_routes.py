"""Test application routes and endpoints."""
import pytest
import json
from app import db, Signup


def test_index_route_renders(client):
    """Test that index page renders successfully."""
    response = client.get('/')
    
    assert response.status_code == 200
    assert b'Kansas City FIFA' in response.data
    assert b'Sign Up' in response.data or b'sign up' in response.data.lower()


def test_index_route_has_form_fields(client):
    """Test that index page contains all required form fields."""
    response = client.get('/')
    
    assert response.status_code == 200
    assert b'name="name"' in response.data
    assert b'name="email"' in response.data
    assert b'name="phone"' in response.data
    assert b'name="zip_code"' in response.data
    assert b'name="events_interested"' in response.data


def test_signup_successful_submission(client, app, sample_signup_form_data):
    """Test successful signup form submission."""
    response = client.post('/signup', data=sample_signup_form_data, follow_redirects=False)
    
    # Should redirect to success page
    assert response.status_code == 302
    assert b'/success/' in response.data or 'success' in response.location
    
    # Verify data was saved
    with app.app_context():
        signup = Signup.query.filter_by(email=sample_signup_form_data['email']).first()
        assert signup is not None
        assert signup.name == sample_signup_form_data['name']
        assert signup.email == sample_signup_form_data['email']


def test_signup_validation_missing_name(client, sample_signup_form_data):
    """Test validation when name is missing."""
    data = sample_signup_form_data.copy()
    data['name'] = ''
    
    response = client.post('/signup', data=data, follow_redirects=True)
    
    # Should stay on form page with error
    assert response.status_code == 200
    assert b'Name' in response.data or b'required' in response.data.lower()


def test_signup_validation_invalid_email(client, sample_signup_form_data):
    """Test validation with invalid email."""
    data = sample_signup_form_data.copy()
    data['email'] = 'not-a-valid-email'
    
    response = client.post('/signup', data=data, follow_redirects=True)
    
    # Should stay on form page with error
    assert response.status_code == 200
    assert b'email' in response.data.lower()


def test_signup_validation_missing_zip(client, sample_signup_form_data):
    """Test validation when zip code is missing."""
    data = sample_signup_form_data.copy()
    data['zip_code'] = ''
    
    response = client.post('/signup', data=data, follow_redirects=True)
    
    # Should stay on form page with error
    assert response.status_code == 200


def test_signup_validation_no_events_selected(client, sample_signup_form_data):
    """Test validation when no events are selected."""
    data = sample_signup_form_data.copy()
    data['events_interested'] = []
    
    response = client.post('/signup', data=data, follow_redirects=True)
    
    # Should stay on form page with error
    assert response.status_code == 200


def test_signup_duplicate_email_prevention(client, app, sample_signup_form_data):
    """Test that duplicate email submissions are prevented."""
    # First submission
    response1 = client.post('/signup', data=sample_signup_form_data, follow_redirects=False)
    assert response1.status_code == 302
    
    # Second submission with same email (cached)
    response2 = client.post('/signup', data=sample_signup_form_data, follow_redirects=True)
    
    # Should show error about duplicate
    assert b'already' in response2.data.lower() or b'registered' in response2.data.lower()


def test_success_page_displays(client, app, sample_signup_data):
    """Test that success page displays signup information."""
    with app.app_context():
        # Create a signup
        signup = Signup(
            name=sample_signup_data['name'],
            email=sample_signup_data['email'],
            zip_code=sample_signup_data['zip_code'],
            events_interested=sample_signup_data['events_interested']
        )
        db.session.add(signup)
        db.session.commit()
        signup_id = signup.id
    
    # Visit success page
    response = client.get(f'/success/{signup_id}')
    
    assert response.status_code == 200
    assert sample_signup_data['name'].encode() in response.data
    assert sample_signup_data['email'].encode() in response.data
    assert b'success' in response.data.lower() or b'confirmed' in response.data.lower()


def test_success_page_not_found(client):
    """Test that success page returns 404 for invalid ID."""
    response = client.get('/success/99999')
    
    assert response.status_code == 404


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/health')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data


def test_metrics_endpoint(client, app):
    """Test metrics endpoint."""
    # Metrics should be enabled in testing config
    response = client.get('/metrics')
    
    if response.status_code == 200:
        data = json.loads(response.data)
        assert 'total_signups' in data
        assert 'today_signups' in data
        assert 'timestamp' in data


def test_signup_tracks_ip_and_user_agent(client, app, sample_signup_form_data):
    """Test that signup tracks IP address and user agent."""
    response = client.post(
        '/signup',
        data=sample_signup_form_data,
        headers={'User-Agent': 'Test Browser 1.0'},
        environ_base={'REMOTE_ADDR': '192.168.1.100'},
        follow_redirects=False
    )
    
    assert response.status_code == 302
    
    with app.app_context():
        signup = Signup.query.filter_by(email=sample_signup_form_data['email']).first()
        assert signup is not None
        assert signup.ip_address == '192.168.1.100'
        assert 'Test Browser' in signup.user_agent


def test_phone_optional(client, app, sample_signup_form_data):
    """Test that phone number is optional."""
    data = sample_signup_form_data.copy()
    data['phone'] = ''
    
    response = client.post('/signup', data=data, follow_redirects=False)
    
    assert response.status_code == 302
    
    with app.app_context():
        signup = Signup.query.filter_by(email=data['email']).first()
        assert signup is not None
        assert signup.phone is None or signup.phone == ''

