# Deployment Guide

This guide covers deploying the Kansas City FIFA Signup application to various platforms.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Heroku Deployment](#heroku-deployment)
- [Production Considerations](#production-considerations)

## Prerequisites

### Required Services
- **PostgreSQL 15+** - Primary database
- **Redis 7+** - Caching and message broker
- **Python 3.11+** - Application runtime
- **Twilio Account** - SMS delivery

### Environment Variables
All required environment variables are documented in `.env.example`. Copy this file to `.env` and update with your credentials:

```bash
cp .env.example .env
```

Key variables to configure:
- `SECRET_KEY` - Flask secret key (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- `TWILIO_ACCOUNT_SID` - Your Twilio Account SID
- `TWILIO_AUTH_TOKEN` - Your Twilio Auth Token
- `TWILIO_FROM_NUMBER` - Your Twilio phone number in E.164 format

## Local Development

### Quick Start

```bash
# 1. Run setup script
./scripts/setup.sh

# 2. Update .env with your credentials
nano .env

# 3. Start all services
./scripts/start_local.sh
```

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start Redis
brew services start redis  # macOS
# or
sudo systemctl start redis  # Linux

# Initialize database
export FLASK_APP=app.py
flask db upgrade

# Start Celery worker (in separate terminal)
celery -A app.celery worker --loglevel=info

# Start Flask application
flask run --host=0.0.0.0 --port=5000
```

The application will be available at `http://localhost:5000`

## Docker Deployment

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services included:
- **web**: Flask application (port 5000)
- **db**: PostgreSQL database
- **redis**: Redis cache/broker
- **celery_worker**: Background task processor
- **nginx**: Reverse proxy (port 80)

### Custom Docker Build

```bash
# Build image
docker build -t kcfifa-signup:latest .

# Run with environment variables
docker run -p 5000:5000 \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  -e SECRET_KEY=... \
  kcfifa-signup:latest
```

## Heroku Deployment

### Automated Deployment

```bash
# Run deployment script
./scripts/deploy.sh
```

This script will:
1. Create/configure Heroku app
2. Add PostgreSQL and Redis add-ons
3. Configure environment variables
4. Deploy application
5. Run database migrations
6. Scale dynos

### Manual Heroku Deployment

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add add-ons
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini

# Configure environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set TWILIO_ACCOUNT_SID=your-sid
heroku config:set TWILIO_AUTH_TOKEN=your-token
heroku config:set TWILIO_FROM_NUMBER=your-number
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Run migrations
heroku run flask db upgrade

# Scale dynos
heroku ps:scale web=1 worker=1

# Open application
heroku open
```

### Heroku Configuration

**Required Add-ons:**
- `heroku-postgresql:mini` or higher
- `heroku-redis:mini` or higher

**Recommended Dyno Types:**
- **Web Dynos**: Standard-1X or higher for production
- **Worker Dynos**: Standard-1X or higher for production
- **Quantity**: Scale based on traffic (minimum 2 web, 1 worker)

### Scaling for High Traffic

```bash
# Scale web dynos
heroku ps:scale web=4 worker=2

# Upgrade database
heroku addons:upgrade heroku-postgresql:standard-0

# Upgrade Redis
heroku addons:upgrade heroku-redis:premium-0

# Enable autoscaling (requires paid dynos)
heroku ps:autoscale:enable web \
  --min 2 \
  --max 10 \
  --p95-response-time 500ms
```

## Production Considerations

### Performance Optimization

1. **Database Connection Pooling**
   - Default pool size: 20 connections
   - Adjust `DATABASE_POOL_SIZE` based on traffic
   - Formula: `pool_size = (number_of_dynos * workers_per_dyno) + buffer`

2. **Redis Configuration**
   - Use separate Redis databases for caching, rate limiting, and Celery
   - Enable persistence if using Redis for critical data
   - Consider Redis cluster for high availability

3. **Caching Strategy**
   - Form configuration cached for 10 minutes
   - Email duplicate check cached for 1 hour
   - Adjust `CACHE_DEFAULT_TIMEOUT` based on needs

4. **Worker Configuration**
   - Default: 4 Gunicorn workers with 2 threads each
   - Adjust based on dyno resources: `workers = (2 * num_cores) + 1`
   - Monitor memory usage and adjust accordingly

### Security

1. **Environment Variables**
   - Never commit `.env` file
   - Rotate `SECRET_KEY` regularly
   - Use strong, unique passwords

2. **HTTPS**
   - Heroku provides HTTPS by default
   - Set `FORCE_HTTPS=true` in production
   - Configure proper CORS if needed

3. **Rate Limiting**
   - Default limits in `config.py`
   - Adjust based on expected traffic patterns
   - Monitor for abuse

4. **CSRF Protection**
   - Enabled by default with Flask-WTF
   - 30-minute token expiration
   - Refresh tokens on form errors

### Monitoring

1. **Heroku Metrics**
   ```bash
   # View metrics
   heroku metrics
   
   # View logs
   heroku logs --tail
   ```

2. **Application Metrics**
   - `/health` - Health check endpoint
   - `/metrics` - Application metrics (if enabled)

3. **Sentry Integration**
   - Set `SENTRY_DSN` for error tracking
   - Automatic error reporting and alerting
   - Performance monitoring enabled

4. **Log Aggregation**
   - Consider add-ons: Papertrail, Logentries, or Splunk
   - Structured logging with `structlog`
   - JSON format for easy parsing

### Database Maintenance

```bash
# Backup database
heroku pg:backups:capture
heroku pg:backups:download

# View database info
heroku pg:info

# Run psql console
heroku pg:psql

# View slow queries
heroku pg:diagnose
```

### Testing in Production-Like Environment

```bash
# Create staging app
heroku create your-app-name-staging --remote staging

# Deploy to staging
git push staging main

# Run load tests
locust -f tests/load_test.py --host=https://your-app-staging.herokuapp.com
```

### Rollback

```bash
# View releases
heroku releases

# Rollback to previous release
heroku rollback

# Rollback to specific version
heroku rollback v23
```

## Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Check database status
heroku pg:info

# Reset database connections
heroku pg:killall
```

**2. Redis Connection Errors**
```bash
# Check Redis status
heroku redis:info

# View Redis connection stats
heroku redis:cli --app your-app-name INFO
```

**3. Worker Not Processing Tasks**
```bash
# Check worker logs
heroku logs --ps worker --tail

# Restart worker
heroku ps:restart worker
```

**4. High Memory Usage**
```bash
# Check memory usage
heroku ps

# Reduce workers
heroku config:set WEB_CONCURRENCY=2
```

**5. Slow Response Times**
```bash
# Check application metrics
heroku metrics

# Enable detailed logging
heroku config:set LOG_LEVEL=DEBUG

# Analyze with New Relic or Scout APM
heroku addons:create newrelic:wayne
```

## Support

For issues or questions:
- Check logs: `heroku logs --tail`
- Review metrics: `heroku metrics`
- Contact support: info@kcfifafanfest.com

