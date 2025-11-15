"""
Load testing with Locust for high-traffic scenarios.

Usage:
    locust -f tests/load_test.py --host=http://localhost:5000
    
    # Or with specific parameters:
    locust -f tests/load_test.py --users 1000 --spawn-rate 100 --run-time 5m --host=http://localhost:5000
"""
from locust import HttpUser, task, between, events
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
    
    # Wait between 1 and 3 seconds between tasks
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a simulated user starts."""
        self.csrf_token = None
        logger.info("User started")
    
    @task(10)
    def view_signup_page(self):
        """View the signup form page (most common action)."""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                # Extract CSRF token if present
                if b'csrf_token' in response.content:
                    # Simple extraction (in production, use proper HTML parsing)
                    try:
                        content = response.content.decode('utf-8')
                        start = content.find('name="csrf_token" value="') + len('name="csrf_token" value="')
                        end = content.find('"', start)
                        if start > 0 and end > 0:
                            self.csrf_token = content[start:end]
                    except Exception as e:
                        logger.warning(f"Could not extract CSRF token: {e}")
                
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(5)
    def submit_signup_form(self):
        """Submit a signup form (less common than just viewing)."""
        # Generate random user data
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        email = f"{first_name.lower()}.{last_name.lower()}.{random.randint(1000, 9999)}@example.com"
        phone = f"555{random.randint(1000000, 9999999)}"
        zip_code = random.choice(ZIP_CODES)
        
        # Select 1-4 random events
        num_events = random.randint(1, 4)
        events_interested = random.sample(EVENTS, num_events)
        
        form_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'zip_code': zip_code,
            'events_interested': events_interested,
        }
        
        if self.csrf_token:
            form_data['csrf_token'] = self.csrf_token
        
        with self.client.post(
            "/signup",
            data=form_data,
            allow_redirects=False,
            catch_response=True
        ) as response:
            if response.status_code in [200, 302]:
                response.success()
            elif response.status_code == 429:
                # Rate limit hit - this is expected under load
                response.failure("Rate limit hit (expected under high load)")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def check_health(self):
        """Check the health endpoint."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    if json_data.get('status') == 'healthy':
                        response.success()
                    else:
                        response.failure("Health check returned unhealthy status")
                except Exception as e:
                    response.failure(f"Could not parse health check response: {e}")
            else:
                response.failure(f"Health check failed with status {response.status_code}")
    
    @task(1)
    def check_metrics(self):
        """Check the metrics endpoint."""
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code in [200, 404]:
                # 404 is acceptable if metrics are disabled
                response.success()
            else:
                response.failure(f"Metrics endpoint returned {response.status_code}")


class BurstTrafficUser(HttpUser):
    """Simulates burst traffic patterns (sudden spikes)."""
    
    wait_time = between(0.1, 0.5)  # Much faster requests
    
    @task
    def rapid_page_views(self):
        """Rapidly view the signup page."""
        self.client.get("/", name="/rapid_view")


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


# Load test scenarios for different traffic patterns
class SteadyTrafficUser(SignupUser):
    """Simulates steady, consistent traffic."""
    wait_time = between(2, 5)
    weight = 7  # 70% of users


class PeakTrafficUser(SignupUser):
    """Simulates peak traffic (e.g., right after announcement)."""
    wait_time = between(0.5, 2)
    weight = 3  # 30% of users

