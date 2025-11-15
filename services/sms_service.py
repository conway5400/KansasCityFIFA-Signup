"""
SMS Service for sending confirmation messages via Twilio
Optimized for high-volume sending with proper error handling
"""
import os
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import structlog

logger = structlog.get_logger(__name__)


class SMSService:
    """High-performance SMS service with Twilio."""
    
    def __init__(self):
        """Initialize Twilio client with credentials."""
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.from_number = os.environ.get('TWILIO_FROM_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.warning("twilio_not_configured", 
                          message="SMS service not fully configured - check environment variables")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
    
    def send_confirmation_sms(self, to_number, name):
        """
        Send confirmation SMS to user.
        
        Args:
            to_number (str): Recipient phone number
            name (str): User's name for personalization
            
        Returns:
            dict: Result with status and message ID
        """
        if not self.client:
            logger.error("sms_service_not_configured")
            raise Exception("SMS service not configured")
        
        # Clean phone number
        to_number = self.clean_phone_number(to_number)
        
        # Create personalized message
        message_body = self.create_confirmation_message(name)
        
        try:
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=to_number
            )
            
            logger.info("sms_sent_successfully", 
                       message_sid=message.sid,
                       to_number=to_number,
                       status=message.status)
            
            return {
                'success': True,
                'message_id': message.sid,
                'status': message.status,
                'to_number': to_number
            }
            
        except TwilioException as e:
            logger.error("twilio_sms_error", 
                        error_code=e.code,
                        error_message=str(e),
                        to_number=to_number)
            raise Exception(f"SMS sending failed: {e.msg}")
        
        except Exception as e:
            logger.error("sms_send_general_error", 
                        error=str(e),
                        to_number=to_number)
            raise Exception(f"SMS sending failed: {str(e)}")
    
    def clean_phone_number(self, phone):
        """
        Clean and format phone number for Twilio.
        
        Args:
            phone (str): Raw phone number
            
        Returns:
            str: Cleaned phone number with country code
        """
        if not phone:
            raise ValueError("Phone number is required")
        
        # Remove all non-digit characters
        digits_only = ''.join(filter(str.isdigit, phone))
        
        # Add country code if missing (assume US)
        if len(digits_only) == 10:
            digits_only = '1' + digits_only
        elif len(digits_only) == 11 and digits_only.startswith('1'):
            pass  # Already has country code
        else:
            raise ValueError(f"Invalid phone number format: {phone}")
        
        return '+' + digits_only
    
    def create_confirmation_message(self, name):
        """
        Create personalized confirmation message.
        
        Args:
            name (str): User's name
            
        Returns:
            str: Formatted confirmation message
        """
        message = f"""🎉 Hey {name}!

Thanks for signing up for the Kansas City FIFA Fan Fest! 

Your registration is confirmed and we're excited to see you there! ⚽

Keep an eye out for updates as we get closer to the event.

Need to make changes? Reply STOP to unsubscribe.

#KCFIFAFest #WorldCup"""
        
        return message
    
    def get_message_status(self, message_sid):
        """
        Get delivery status of a sent message.
        
        Args:
            message_sid (str): Twilio message SID
            
        Returns:
            dict: Message status information
        """
        if not self.client:
            raise Exception("SMS service not configured")
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                'status': message.status,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'date_sent': message.date_sent,
                'date_updated': message.date_updated
            }
            
        except TwilioException as e:
            logger.error("twilio_status_check_error", 
                        message_sid=message_sid,
                        error=str(e))
            raise Exception(f"Status check failed: {e.msg}")


# Global SMS service instance
sms_service = SMSService()


def send_confirmation_sms(phone_number, name):
    """
    Convenience function for sending confirmation SMS.
    
    Args:
        phone_number (str): Recipient phone number
        name (str): User's name
        
    Returns:
        dict: Send result
    """
    return sms_service.send_confirmation_sms(phone_number, name)
