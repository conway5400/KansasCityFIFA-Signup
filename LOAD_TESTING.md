# Load Testing Guide

This guide explains how to run load tests against your Heroku-deployed application.

## Overview

The application uses **Locust** for load testing. Locust is a Python-based load testing tool that simulates users hitting your application endpoints.

## Prerequisites

1. **Deploy your application to Heroku** (see DEPLOYMENT.md)
2. **Install Locust locally** (already in requirements.txt):
   ```bash
   pip install locust
   ```

## Quick Start

### 1. Get Your Heroku App URL

After deploying, your app will be available at:
```
https://your-app-name.herokuapp.com
```

### 2. Run Load Tests

From your local machine, run:

```bash
# Basic load test (opens web UI)
locust -f tests/load_test.py --host=https://your-app-name.herokuapp.com

# Then open http://localhost:8089 in your browser
# Set number of users and spawn rate, then click "Start Swarming"
```

### 3. Command-Line Load Test (No UI)

```bash
# Run with specific parameters
locust -f tests/load_test.py \
  --host=https://your-app-name.herokuapp.com \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless
```

**Parameters:**
- `--users`: Total number of concurrent users
- `--spawn-rate`: Users spawned per second
- `--run-time`: How long to run the test (e.g., `5m`, `1h`)
- `--headless`: Run without web UI

## Load Test Scenarios

The load test (`tests/load_test.py`) includes:

1. **SignupUser**: Simulates normal user behavior
   - Views signup page (10x weight)
   - Submits signup form (5x weight)
   - Checks health endpoint (1x weight)
   - Checks metrics endpoint (1x weight)

2. **BurstTrafficUser**: Simulates sudden traffic spikes
   - Rapid page views

3. **SteadyTrafficUser**: Consistent, steady traffic (70% of users)

4. **PeakTrafficUser**: Peak traffic simulation (30% of users)

## Example Load Test Scenarios

### Light Load Test (Development)
```bash
locust -f tests/load_test.py \
  --host=https://your-app-name.herokuapp.com \
  --users 10 \
  --spawn-rate 2 \
  --run-time 2m \
  --headless
```

### Medium Load Test (Staging)
```bash
locust -f tests/load_test.py \
  --host=https://your-app-name.herokuapp.com \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless
```

### Heavy Load Test (Production Simulation)
```bash
locust -f tests/load_test.py \
  --host=https://your-app-name.herokuapp.com \
  --users 500 \
  --spawn-rate 50 \
  --run-time 10m \
  --headless
```

### Stress Test (Find Breaking Point)
```bash
locust -f tests/load_test.py \
  --host=https://your-app-name.herokuapp.com \
  --users 1000 \
  --spawn-rate 100 \
  --run-time 15m \
  --headless
```

## Monitoring During Load Tests

### Heroku Metrics

While running load tests, monitor your Heroku app:

```bash
# View real-time metrics
heroku metrics --app your-app-name

# View logs
heroku logs --tail --app your-app-name

# Check dyno status
heroku ps --app your-app-name
```

### Key Metrics to Watch

1. **Response Time**: Should stay under 500ms for most requests
2. **Error Rate**: Should be < 1%
3. **Dyno Memory**: Should not exceed dyno limits
4. **Database Connections**: Monitor connection pool usage
5. **Redis Memory**: Check Redis addon usage

## Interpreting Results

### Good Performance Indicators

- ✅ Average response time < 500ms
- ✅ 95th percentile response time < 1s
- ✅ Error rate < 1%
- ✅ No memory leaks (stable memory usage)
- ✅ Database connection pool not exhausted

### Warning Signs

- ⚠️ Response times increasing over time
- ⚠️ Error rate > 1%
- ⚠️ High memory usage
- ⚠️ Rate limiting being hit frequently (429 errors)

### Critical Issues

- ❌ Error rate > 5%
- ❌ Response times > 5s
- ❌ Dyno crashes or restarts
- ❌ Database connection errors

## Scaling for Load

If load tests reveal performance issues:

### Scale Web Dynos
```bash
heroku ps:scale web=2 --app your-app-name
heroku ps:scale web=4 --app your-app-name  # For higher traffic
```

### Scale Worker Dynos
```bash
heroku ps:scale worker=2 --app your-app-name
```

### Upgrade Database
```bash
heroku addons:upgrade heroku-postgresql:standard-0 --app your-app-name
```

### Upgrade Redis
```bash
heroku addons:upgrade heroku-redis:premium-0 --app your-app-name
```

## Best Practices

1. **Start Small**: Begin with low user counts and gradually increase
2. **Test During Off-Peak**: Run heavy load tests during low-traffic periods
3. **Monitor Costs**: Heroku charges for dyno hours - be mindful of test duration
4. **Use Staging**: Test on a staging environment before production
5. **Document Results**: Keep records of load test results for comparison

## Troubleshooting

### Connection Errors

If you see connection errors:
- Check Heroku app is running: `heroku ps --app your-app-name`
- Verify app URL is correct
- Check firewall/network settings

### Rate Limiting

If you hit rate limits (429 errors):
- This is expected under high load
- Adjust rate limits in `config.py` if needed
- Consider increasing limits for load testing

### Timeout Errors

If requests timeout:
- Check Heroku logs for errors
- Verify database and Redis connections
- Consider scaling dynos

## Load Test Script

The load test script (`tests/load_test.py`) includes:

- Random user data generation
- CSRF token handling
- Multiple user behavior patterns
- Health check monitoring
- Metrics endpoint testing

You can customize the load test by editing `tests/load_test.py`.

## Next Steps

After load testing:

1. Review results and identify bottlenecks
2. Optimize slow endpoints
3. Scale infrastructure as needed
4. Re-test to verify improvements
5. Document performance characteristics

## Additional Resources

- [Locust Documentation](https://docs.locust.io/)
- [Heroku Performance Metrics](https://devcenter.heroku.com/articles/metrics)
- [Heroku Scaling Guide](https://devcenter.heroku.com/articles/scaling)

