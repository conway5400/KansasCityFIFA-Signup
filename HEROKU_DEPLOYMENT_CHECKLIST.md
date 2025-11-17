# Heroku Deployment Checklist

This checklist will guide you through deploying the Kansas City FIFA Signup application to Heroku.

## Prerequisites

✅ **GitHub CLI** - Already available  
✅ **Heroku CLI** - Already available  
✅ **Git repository** - Your code should be committed to git

## Pre-Deployment Checklist

### 1. Verify Application Files

- [x] `Procfile` - Configured for web and worker dynos
- [x] `requirements.txt` - All dependencies listed
- [x] `runtime.txt` - Python version specified (3.11.6)
- [x] `app.json` - Heroku app configuration
- [x] `.env.example` - Environment variables documented

### 2. Required Environment Variables

Make sure you have these values ready:

- [ ] **SECRET_KEY** - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] **TWILIO_ACCOUNT_SID** - From your Twilio account
- [ ] **TWILIO_AUTH_TOKEN** - From your Twilio account  
- [ ] **TWILIO_FROM_NUMBER** - Your Twilio phone number (E.164 format: +15551234567)

### 3. Code Status

- [x] Celery configuration fixed (`celery_app.py` updated)
- [x] Config handles Heroku DATABASE_URL (postgres:// → postgresql://)
- [x] Config uses REDIS_URL for Celery if CELERY_BROKER_URL not set
- [x] Procfile uses correct celery command (`celery_app`)

## Deployment Steps

### Step 1: Login to Heroku

```bash
heroku login
```

### Step 2: Create Heroku App (or use existing)

**Option A: Create new app**
```bash
heroku create your-app-name
```

**Option B: Use existing app**
```bash
# If app already exists, add remote
git remote add heroku https://git.heroku.com/your-app-name.git
```

### Step 3: Add Required Add-ons

```bash
# PostgreSQL database
heroku addons:create heroku-postgresql:mini --app your-app-name

# Redis (for caching and Celery)
heroku addons:create heroku-redis:mini --app your-app-name
```

**Note:** These add-ons automatically set `DATABASE_URL` and `REDIS_URL` environment variables.

### Step 4: Set Environment Variables

```bash
# Set required variables
heroku config:set SECRET_KEY=your-generated-secret-key --app your-app-name
heroku config:set TWILIO_ACCOUNT_SID=your-twilio-sid --app your-app-name
heroku config:set TWILIO_AUTH_TOKEN=your-twilio-token --app your-app-name
heroku config:set TWILIO_FROM_NUMBER=+15551234567 --app your-app-name
heroku config:set FLASK_ENV=production --app your-app-name
heroku config:set FLASK_APP=app.py --app your-app-name

# Optional: Set performance tuning variables
heroku config:set DATABASE_POOL_SIZE=20 --app your-app-name
heroku config:set DATABASE_MAX_OVERFLOW=30 --app your-app-name
heroku config:set LOG_LEVEL=INFO --app your-app-name
heroku config:set METRICS_ENABLED=true --app your-app-name
```

### Step 5: Deploy Application

```bash
# Make sure you're on main/master branch
git checkout main  # or master

# Push to Heroku
git push heroku main
# or
git push heroku master
```

### Step 6: Run Database Migrations

Migrations should run automatically via the `release` phase in Procfile, but you can also run manually:

```bash
heroku run flask db upgrade --app your-app-name
```

### Step 7: Scale Dynos

```bash
# Scale web and worker dynos
heroku ps:scale web=1 worker=1 --app your-app-name
```

### Step 8: Verify Deployment

```bash
# Open your app
heroku open --app your-app-name

# Check logs
heroku logs --tail --app your-app-name

# Check dyno status
heroku ps --app your-app-name

# Test health endpoint
curl https://your-app-name.herokuapp.com/health
```

## Post-Deployment Verification

### Check Application Status

- [ ] App loads at `https://your-app-name.herokuapp.com`
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Form displays correctly
- [ ] Can submit a test signup
- [ ] Worker dyno is running (check `heroku ps`)

### Check Logs

```bash
# View all logs
heroku logs --tail --app your-app-name

# View web logs only
heroku logs --ps web --tail --app your-app-name

# View worker logs only
heroku logs --ps worker --tail --app your-app-name
```

### Common Issues to Check

1. **Database Connection**: Check logs for PostgreSQL connection errors
2. **Redis Connection**: Check logs for Redis connection errors
3. **Celery Worker**: Verify worker dyno is processing tasks
4. **Environment Variables**: Verify all required vars are set (`heroku config`)

## Load Testing Setup

Once deployed, you can run load tests against your Heroku app:

### Install Locust (if not already installed)

```bash
pip install locust
```

### Run Load Test

```bash
# Interactive mode (opens web UI)
locust -f tests/load_test.py --host=https://your-app-name.herokuapp.com

# Headless mode (command line)
locust -f tests/load_test.py \
  --host=https://your-app-name.herokuapp.com \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless
```

See `LOAD_TESTING.md` for detailed load testing instructions.

## Monitoring

### View Metrics

```bash
# Real-time metrics
heroku metrics --app your-app-name

# Detailed metrics dashboard
heroku metrics:web --app your-app-name
```

### Useful Commands

```bash
# View config vars
heroku config --app your-app-name

# View add-ons
heroku addons --app your-app-name

# View recent releases
heroku releases --app your-app-name

# Restart app
heroku restart --app your-app-name

# Scale dynos
heroku ps:scale web=2 worker=1 --app your-app-name
```

## Troubleshooting

### App Won't Start

1. Check logs: `heroku logs --tail --app your-app-name`
2. Verify Procfile syntax
3. Check environment variables: `heroku config --app your-app-name`
4. Verify add-ons are provisioned: `heroku addons --app your-app-name`

### Database Errors

1. Verify PostgreSQL addon: `heroku addons --app your-app-name`
2. Check DATABASE_URL: `heroku config:get DATABASE_URL --app your-app-name`
3. Run migrations: `heroku run flask db upgrade --app your-app-name`

### Worker Not Running

1. Check worker logs: `heroku logs --ps worker --tail --app your-app-name`
2. Verify worker dyno is scaled: `heroku ps --app your-app-name`
3. Check Redis connection: Verify REDIS_URL is set

### High Error Rate

1. Check application logs for errors
2. Monitor metrics: `heroku metrics --app your-app-name`
3. Consider scaling dynos: `heroku ps:scale web=2 --app your-app-name`

## Quick Reference

### Your App URL
```
https://your-app-name.herokuapp.com
```

### Key Endpoints
- **Home**: `/`
- **Health Check**: `/health`
- **Metrics**: `/metrics`

### Important Commands
```bash
# Deploy
git push heroku main

# View logs
heroku logs --tail

# Run migrations
heroku run flask db upgrade

# Scale
heroku ps:scale web=1 worker=1

# Open app
heroku open
```

## Next Steps

1. ✅ Deploy to Heroku
2. ✅ Verify deployment
3. ✅ Run load tests (see `LOAD_TESTING.md`)
4. ✅ Monitor performance
5. ✅ Scale as needed

## Support

- Heroku Documentation: https://devcenter.heroku.com/
- Application Logs: `heroku logs --tail`
- Heroku Status: https://status.heroku.com/

