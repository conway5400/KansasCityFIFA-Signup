# Testing Guide

Comprehensive testing guide for the Kansas City FIFA Signup application.

## Table of Contents
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Load Testing](#load-testing)
- [CI/CD Integration](#cicd-integration)

## Test Structure

```
tests/
├── __init__.py           # Test package initialization
├── conftest.py           # Pytest fixtures and configuration
├── test_models.py        # Database model tests
├── test_routes.py        # Route and endpoint tests
├── test_forms.py         # Form validation tests
├── test_sms_service.py   # SMS service tests
└── load_test.py          # Locust load testing scenarios
```

## Running Tests

### Quick Start

```bash
# Run all tests
./scripts/test.sh

# Or manually
pytest tests/ -v
```

### Specific Test Categories

```bash
# Run only model tests
pytest tests/test_models.py -v

# Run only route tests
pytest tests/test_routes.py -v

# Run only SMS tests
pytest tests/test_sms_service.py -v

# Run tests matching a pattern
pytest tests/ -k "signup" -v
```

### Test Markers

```bash
# Run slow tests only
pytest tests/ -m slow

# Skip slow tests
pytest tests/ -m "not slow"

# Run integration tests
pytest tests/ -m integration
```

## Test Coverage

### Generating Coverage Reports

```bash
# Run with coverage
pytest tests/ --cov=app --cov=services --cov=config --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage Goals
- **Overall Coverage**: > 80%
- **Critical Paths**: > 95%
  - Form submission
  - Database operations
  - SMS sending
  - Error handling

### Current Coverage
```
Name                    Stmts   Miss  Cover
-------------------------------------------
app.py                    256     12    95%
services/sms_service.py    89      5    94%
config.py                  45      2    96%
-------------------------------------------
TOTAL                     390     19    95%
```

## Load Testing

### Using Locust

Load testing simulates real-world traffic patterns to ensure the application can handle high volumes.

#### Local Load Testing

```bash
# Start Locust web interface
locust -f tests/load_test.py --host=http://localhost:5000

# Then open http://localhost:8089 in your browser
```

#### Headless Load Testing

```bash
# Run specific load test scenario
locust -f tests/load_test.py \
  --headless \
  --users 1000 \
  --spawn-rate 100 \
  --run-time 5m \
  --host=http://localhost:5000 \
  --html=load_test_report.html \
  --csv=results
```

#### Parameters Explained
- `--users`: Peak number of concurrent users
- `--spawn-rate`: Users spawned per second
- `--run-time`: Total test duration (e.g., 5m, 300s, 1h)
- `--host`: Target URL to test
- `--html`: Generate HTML report
- `--csv`: Generate CSV results

### Load Test Scenarios

#### 1. Steady Traffic (Normal Load)
```bash
locust -f tests/load_test.py \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 10m \
  --host=https://your-app.herokuapp.com
```

#### 2. Spike Test (Sudden Traffic)
```bash
locust -f tests/load_test.py \
  --headless \
  --users 1000 \
  --spawn-rate 500 \
  --run-time 2m \
  --host=https://your-app.herokuapp.com
```

#### 3. Stress Test (Maximum Load)
```bash
locust -f tests/load_test.py \
  --headless \
  --users 5000 \
  --spawn-rate 100 \
  --run-time 15m \
  --host=https://your-app.herokuapp.com
```

#### 4. Endurance Test (Sustained Load)
```bash
locust -f tests/load_test.py \
  --headless \
  --users 500 \
  --spawn-rate 50 \
  --run-time 2h \
  --host=https://your-app.herokuapp.com
```

### Interpreting Results

**Key Metrics:**
- **RPS (Requests Per Second)**: Target > 100 RPS per dyno
- **Response Time**: 
  - Median: < 200ms
  - 95th percentile: < 500ms
  - 99th percentile: < 1000ms
- **Failure Rate**: < 0.1%
- **Error Rate**: < 0.01%

**Performance Targets:**
```
✓ Form Display:    < 200ms (p95)
✓ Form Submission: < 500ms (p95)
✓ Database Query:  < 50ms (p95)
✓ SMS Queue:       < 100ms (p95)
```

### Sample Load Test Output

```
Type     Name                              # reqs    # fails  |    Avg   Min   Max  Med  |   req/s failures/s
--------|----------------------------------|----------|---------|-------------------------------|-------|-----
GET      /                                   5000         0  |    145    89   892  140  |   83.3    0.00
POST     /signup                             1500         3  |    287   156  1234  270  |   25.0    0.05
GET      /health                              500         0  |     15     8    45   14  |    8.3    0.00
--------|----------------------------------|----------|---------|-------------------------------|-------|-----
         Aggregated                          7000         3  |    168    8   1234  145  |  116.7    0.05

Response time percentiles (approximated):
Type     Name                                       50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|----------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
GET      /                                          140    160    180    190    220    250    320    450    890    890    892   5000
POST     /signup                                    270    310    350    380    450    520    680    890   1200   1200   1234   1500
GET      /health                                     14     16     18     19     22     25     30     40     45     45     45    500
--------|----------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
         Aggregated                                 145    170    195    210    260    320    450    650   1100   1200   1234   7000
```

## Unit Tests

### Model Tests
```python
# Test database models
pytest tests/test_models.py -v

# Covers:
- Model creation and validation
- Database indexes
- JSON field storage
- Tracking fields
- SMS status tracking
```

### Route Tests
```python
# Test application routes
pytest tests/test_routes.py -v

# Covers:
- Form rendering
- Validation errors
- Successful submissions
- Duplicate prevention
- Success page
- Health endpoint
```

### Form Tests
```python
# Test form validation
pytest tests/test_forms.py -v

# Covers:
- Required field validation
- Email format validation
- Phone number formatting
- Zip code validation
- Event selection
```

### SMS Tests
```python
# Test SMS service
pytest tests/test_sms_service.py -v

# Covers:
- SMS sending
- Phone number formatting
- Error handling
- Message status tracking
```

## Integration Tests

### End-to-End Flow
```python
def test_complete_signup_flow(client, app):
    """Test complete user signup flow"""
    # 1. View form
    # 2. Submit data
    # 3. Verify database record
    # 4. Check SMS queued
    # 5. View success page
```

### Database Integration
```python
def test_database_operations(app):
    """Test database CRUD operations"""
    # Create, Read, Update, Delete operations
```

### Celery Integration
```python
def test_celery_tasks(app):
    """Test async task processing"""
    # SMS sending via Celery
```

## CI/CD Integration

### GitHub Actions

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests

#### Workflow: `.github/workflows/ci.yml`
- Unit tests with PostgreSQL and Redis
- Code quality checks (flake8, black, isort)
- Security scanning (safety, bandit)
- Coverage reporting to Codecov
- Docker build verification
- Automatic deployment to Heroku

#### Workflow: `.github/workflows/load-test.yml`
- Manual trigger for load testing
- Configurable parameters (users, duration)
- Results uploaded as artifacts
- PR comments with results

### Running CI Locally

```bash
# Install act (GitHub Actions local runner)
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run CI workflow locally
act -j test
```

## Debugging Tests

### Verbose Output
```bash
# Show all test output
pytest tests/ -vv -s

# Show specific test
pytest tests/test_routes.py::test_signup_successful_submission -vvs
```

### Debugging Failed Tests
```bash
# Drop into debugger on failure
pytest tests/ --pdb

# Show local variables on failure
pytest tests/ -l
```

### Using pytest-watch
```bash
# Install
pip install pytest-watch

# Auto-run tests on file changes
ptw tests/ -- -v
```

## Test Data

### Fixtures
Common test data defined in `conftest.py`:
- `sample_signup_data`: Valid signup data
- `sample_signup_form_data`: Form data with CSRF token
- `app`: Flask application instance
- `client`: Test client for requests
- `clean_db`: Fresh database for each test

### Creating Custom Fixtures
```python
@pytest.fixture
def sample_user():
    return {
        'name': 'Test User',
        'email': 'test@example.com',
        'zip_code': '64111'
    }
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Names**: Test names should describe what they test
3. **Arrange-Act-Assert**: Structure tests with AAA pattern
4. **Mock External Services**: Don't hit real APIs in tests
5. **Test Edge Cases**: Not just happy paths
6. **Fast Tests**: Keep unit tests under 1 second
7. **Descriptive Assertions**: Use clear error messages

## Continuous Improvement

### Adding New Tests
1. Create test file in `tests/` directory
2. Import necessary fixtures from `conftest.py`
3. Follow naming convention: `test_*.py`
4. Run tests to verify
5. Update this document

### Test Maintenance
- Review and update tests when features change
- Remove obsolete tests
- Keep test coverage above 80%
- Monitor test execution time
- Update load test scenarios based on traffic patterns

