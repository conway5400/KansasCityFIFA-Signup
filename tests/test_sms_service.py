"""Test SMS service functionality."""
import pytest
from unittest.mock import Mock, patch
from services.sms_service import SMSService


@pytest.fixture
def mock_twilio_client():
    """Mock Twilio client for testing."""
    with patch('services.sms_service.Client') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Mock messages.create() method
        mock_message = Mock()
        mock_message.sid = 'SM123456789'
        mock_message.status = 'queued'
        mock_instance.messages.create.return_value = mock_message
        
        yield mock_instance


def test_sms_service_initialization():
    """Test SMS service initializes correctly."""
    with patch.dict('os.environ', {
        'TWILIO_ACCOUNT_SID': 'AC123',
        'TWILIO_AUTH_TOKEN': 'token123',
        'TWILIO_FROM_NUMBER': '+15551234567'
    }):
        service = SMSService()
        assert service.account_sid == 'AC123'
        assert service.auth_token == 'token123'
        assert service.from_number == '+15551234567'


def test_sms_service_missing_credentials():
    """Test SMS service handles missing credentials."""
    with patch.dict('os.environ', {}, clear=True):
        service = SMSService()
        assert service.client is None


def test_clean_phone_number_10_digits():
    """Test cleaning 10-digit US phone number."""
    service = SMSService()
    
    result = service.clean_phone_number('5551234567')
    assert result == '+15551234567'
    
    result = service.clean_phone_number('(555) 123-4567')
    assert result == '+15551234567'
    
    result = service.clean_phone_number('555-123-4567')
    assert result == '+15551234567'


def test_clean_phone_number_11_digits():
    """Test cleaning 11-digit phone number with country code."""
    service = SMSService()
    
    result = service.clean_phone_number('15551234567')
    assert result == '+15551234567'
    
    result = service.clean_phone_number('+15551234567')
    assert result == '+15551234567'


def test_clean_phone_number_invalid():
    """Test that invalid phone numbers raise error."""
    service = SMSService()
    
    with pytest.raises(ValueError):
        service.clean_phone_number('123')  # Too short
    
    with pytest.raises(ValueError):
        service.clean_phone_number('12345678901234')  # Too long
    
    with pytest.raises(ValueError):
        service.clean_phone_number('')  # Empty


def test_create_confirmation_message():
    """Test creating personalized confirmation message."""
    service = SMSService()
    
    message = service.create_confirmation_message('John Doe')
    
    assert 'John Doe' in message
    assert 'Kansas City FIFA' in message
    assert 'confirmed' in message.lower()


@patch.dict('os.environ', {
    'TWILIO_ACCOUNT_SID': 'AC123',
    'TWILIO_AUTH_TOKEN': 'token123',
    'TWILIO_FROM_NUMBER': '+15551234567'
})
def test_send_confirmation_sms_success(mock_twilio_client):
    """Test successful SMS sending."""
    service = SMSService()
    service.client = mock_twilio_client
    
    result = service.send_confirmation_sms('+15559876543', 'Jane Smith')
    
    assert result['success'] is True
    assert result['message_id'] == 'SM123456789'
    assert result['status'] == 'queued'
    assert result['to_number'] == '+15559876543'
    
    # Verify Twilio client was called
    mock_twilio_client.messages.create.assert_called_once()


@patch.dict('os.environ', {
    'TWILIO_ACCOUNT_SID': 'AC123',
    'TWILIO_AUTH_TOKEN': 'token123',
    'TWILIO_FROM_NUMBER': '+15551234567'
})
def test_send_confirmation_sms_twilio_error():
    """Test handling Twilio API errors."""
    from twilio.base.exceptions import TwilioException
    
    with patch('services.sms_service.Client') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Mock Twilio error
        error = TwilioException(status=400, uri='', msg='Invalid phone number', code=21211)
        mock_instance.messages.create.side_effect = error
        
        service = SMSService()
        
        with pytest.raises(Exception) as exc_info:
            service.send_confirmation_sms('+15559876543', 'Jane Smith')
        
        assert 'SMS sending failed' in str(exc_info.value)


def test_send_confirmation_sms_not_configured():
    """Test sending SMS when service is not configured."""
    with patch.dict('os.environ', {}, clear=True):
        service = SMSService()
        
        with pytest.raises(Exception) as exc_info:
            service.send_confirmation_sms('+15559876543', 'Jane Smith')
        
        assert 'not configured' in str(exc_info.value).lower()


@patch.dict('os.environ', {
    'TWILIO_ACCOUNT_SID': 'AC123',
    'TWILIO_AUTH_TOKEN': 'token123',
    'TWILIO_FROM_NUMBER': '+15551234567'
})
def test_get_message_status(mock_twilio_client):
    """Test retrieving message status."""
    mock_message = Mock()
    mock_message.status = 'delivered'
    mock_message.error_code = None
    mock_message.error_message = None
    mock_message.date_sent = '2024-01-01T12:00:00Z'
    mock_message.date_updated = '2024-01-01T12:00:05Z'
    
    mock_twilio_client.messages.return_value.fetch.return_value = mock_message
    
    service = SMSService()
    service.client = mock_twilio_client
    
    result = service.get_message_status('SM123456789')
    
    assert result['status'] == 'delivered'
    assert result['error_code'] is None
    assert result['error_message'] is None

