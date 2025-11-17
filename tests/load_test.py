"""
Load testing with Locust for signup form testing.

Usage:
    locust -f tests/load_test.py --host=https://kc-fifa-signup-fc03fc97207f.herokuapp.com
    
    Then open http://localhost:8089 in your browser to control the test.
"""
from locust import HttpUser, task, between, events
from bs4 import BeautifulSoup
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Sample data for load testing
FIRST_NAMES = ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'Robert', 'Lisa', 
               'William', 'Mary', 'James', 'Patricia', 'Christopher', 'Jennifer', 'Daniel']

LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
              'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson']

EVENTS = [
    'World Cup Viewing Parties',
    'Skills Challenge & Games',
    'Photo Booth Experience',
    'Food Truck Festival',
    'Live Music & Entertainment',
    'Meet & Greet with Players',
    'FIFA Merchandise Shopping',
    'Kids Zone Activities'
]

ZIP_CODES = ['64111', '64112', '64113', '64114', '64115', '64116', '64117', '64118', 
             '64119', '64120', '64121', '64122', '64123', '64124', '64125']


class SignupUser(HttpUser):
    """Simulates a user signing up for the FIFA Fan Fest."""
    
    # Wait between 2 and 5 seconds between tasks (realistic user behavior)
    wait_time = between(2, 5)
    
    def on_start(self):
        """Called when a simulated user starts."""
        # Locust's HttpUser maintains cookies automatically between requests
        # We don't need to store them manually - each user gets a fresh session
        pass
    
    @task(3)
    def view_signup_page(self):
        """View the signup form page."""
        response = self.client.get("/", name="GET / (View Signup Form)")
        if response.status_code != 200:
            logger.warning(f"Failed to load signup page: {response.status_code}")
    
    @task(10)
    def submit_signup_form(self):
        """Submit a signup form - this is the main action we're testing."""
        # Always get a fresh form page right before submitting
        # This ensures the CSRF token and session cookie match
        form_response = self.client.get("/", name="GET / (Get Form for CSRF)")
        if form_response.status_code != 200:
            logger.warning(f"Failed to get form page: {form_response.status_code}")
            return
        
        # Extract CSRF token from the fresh form
        try:
            soup = BeautifulSoup(form_response.text, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrf_token'})
            if not csrf_input or not csrf_input.get('value'):
                logger.warning("Could not find CSRF token in form")
                return
            csrf_token = csrf_input['value']
        except Exception as e:
            logger.warning(f"Error parsing CSRF token: {e}")
            return
        
        # Generate unique user data
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        # Use timestamp + random to ensure unique emails
        import time
        email = f"loadtest.{int(time.time())}.{random.randint(1000, 9999)}.{first_name.lower()}.{last_name.lower()}@loadtest.example.com"
        phone = f"555{random.randint(1000000, 9999999)}"
        zip_code = random.choice(ZIP_CODES)
        
        # Select 1-4 random events (must match exact event names from form)
        num_events = random.randint(1, min(4, len(EVENTS)))
        selected_events = random.sample(EVENTS, num_events)
        
        # Build form data
        # Flask-WTF MultiCheckboxField expects multiple values with the same name
        # We'll use a list of tuples or send multiple values
        form_data = [
            ('csrf_token', csrf_token),
            ('name', name),
            ('email', email),
            ('phone', phone),  # Optional, but we'll include it
            ('zip_code', zip_code),
        ]
        
        # Add each selected event - Flask-WTF expects multiple values with same name
        for event in selected_events:
            form_data.append(('events_interested', event))
        
        headers = {
            'Referer': f'{self.host}/',
        }
        
        # Locust's HttpUser automatically maintains cookies between requests
        # The session cookie from the GET request above will be included automatically
        with self.client.post(
            "/signup",
            data=form_data,
            headers=headers,
            catch_response=True,
            name="POST /signup (Submit Form)"
        ) as response:
            # Check for successful submission (redirect to success page)
            if response.status_code == 302:
                # Check if redirect location contains 'success'
                location = response.headers.get('Location', '')
                if 'success' in location.lower():
                    response.success()
                    logger.info(f"Successfully submitted signup for {email}")
                else:
                    response.failure(f"Unexpected redirect location: {location}")
            elif response.status_code == 200:
                # Might be showing form again with errors
                if 'error' in response.text.lower() or 'already been registered' in response.text.lower():
                    response.failure("Form submission returned error page")
                else:
                    # Could be success page shown directly
                    response.success()
            elif response.status_code == 429:
                response.failure("Rate limit exceeded (429)")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts."""
    logger.info("=" * 80)
    logger.info("LOAD TEST STARTED")
    logger.info(f"Target host: {environment.host}")
    logger.info("=" * 80)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops."""
    logger.info("=" * 80)
    logger.info("LOAD TEST COMPLETED")
    logger.info(f"Total requests: {environment.stats.total.num_requests}")
    logger.info(f"Total failures: {environment.stats.total.num_failures}")
    
    if environment.stats.total.num_requests > 0:
        failure_rate = (environment.stats.total.num_failures / environment.stats.total.num_requests) * 100
        logger.info(f"Failure rate: {failure_rate:.2f}%")
        
        if environment.stats.total.avg_response_time:
            logger.info(f"Average response time: {environment.stats.total.avg_response_time:.2f}ms")
        
        if environment.stats.total.max_response_time:
            logger.info(f"Max response time: {environment.stats.total.max_response_time:.2f}ms")
    
    logger.info("=" * 80)
