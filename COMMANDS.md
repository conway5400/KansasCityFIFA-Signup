# 📝 Command Reference

Quick reference for all commands you'll need.

## 🚀 Quick Deploy (Recommended)

```bash
# 1. Authenticate services
gh auth login
heroku login

# 2. Create GitHub repo
gh repo create KansasCityFIFA-Signup --public --source=. --remote=origin --push

# 3. Deploy to Heroku (automated)
./scripts/deploy.sh

# Done! Your app is live 🎉
```

## 📦 Local Development

### First Time Setup
```bash
# Setup environment
./scripts/setup.sh

# Configure credentials
cp .env.example .env
nano .env  # Add your Twilio credentials
```

### Daily Development
```bash
# Start all services
./scripts/start_local.sh

# App runs at: http://localhost:5000
# Press Ctrl+C to stop
```

### Run Tests
```bash
# All tests with coverage
./scripts/test.sh

# Specific tests
pytest tests/test_routes.py -v
pytest tests/test_models.py::test_signup_model_creation -v

# Watch mode (re-run on changes)
pip install pytest-watch
ptw tests/
```

## 🐳 Docker Commands

### Basic Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Individual Services
```bash
# Just the database
docker-compose up -d db

# Just Redis
docker-compose up -d redis

# Web + worker
docker-compose up -d web celery_worker
```

### Docker Troubleshooting
```bash
# View running containers
docker-compose ps

# Restart a service
docker-compose restart web

# Remove all containers and volumes
docker-compose down -v

# Shell into container
docker-compose exec web bash
```

## 🔧 Git Commands

### Initial Setup (if not done)
```bash
git init
git add -A
git commit -m "Initial commit"
git branch -M main
```

### Daily Git Workflow
```bash
# Check status
git status

# Stage changes
git add .

# Commit
git commit -m "Your commit message"

# Push to GitHub
git push origin main

# Pull latest
git pull origin main
```

### Create Feature Branch
```bash
git checkout -b feature/new-feature
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
```

## 🌐 GitHub Commands

### Create Repository
```bash
# Option 1: Using GitHub CLI
gh repo create KansasCityFIFA-Signup --public --source=. --remote=origin --push

# Option 2: Add remote manually
git remote add origin https://github.com/conway5400/KansasCityFIFA-Signup.git
git push -u origin main
```

### Manage Repository
```bash
# View repo info
gh repo view

# Create issue
gh issue create

# Create pull request
gh pr create

# View CI status
gh run list
gh run view
```

## ☁️ Heroku Commands

### Initial Setup
```bash
# Login
heroku login

# Create app
heroku create kcfifa-signup

# Or create with specific region
heroku create kcfifa-signup --region us
```

### Add-ons
```bash
# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Add Redis
heroku addons:create heroku-redis:mini

# View add-ons
heroku addons

# View specific add-on
heroku pg:info
heroku redis:info
```

### Configuration
```bash
# Set environment variable
heroku config:set SECRET_KEY=your-secret-key

# Set multiple
heroku config:set \
  TWILIO_ACCOUNT_SID=ACxxxx \
  TWILIO_AUTH_TOKEN=xxxx \
  TWILIO_FROM_NUMBER=+15551234567

# View all config
heroku config

# Get specific value
heroku config:get SECRET_KEY

# Remove variable
heroku config:unset VARIABLE_NAME
```

### Deployment
```bash
# Deploy current branch
git push heroku main

# Deploy specific branch
git push heroku feature-branch:main

# View recent releases
heroku releases

# Rollback to previous version
heroku rollback

# Rollback to specific version
heroku rollback v123
```

### Manage Dynos
```bash
# View dyno status
heroku ps

# Scale dynos
heroku ps:scale web=2 worker=1

# Change dyno type
heroku ps:type web=standard-1x

# Restart all dynos
heroku restart

# Restart specific dyno
heroku restart web.1
```

### Logs and Monitoring
```bash
# Tail logs
heroku logs --tail

# Specific process
heroku logs --ps web --tail

# Get last 1000 lines
heroku logs -n 1000

# View metrics
heroku metrics

# Open dashboard
heroku open --app kcfifa-signup
```

### Database Management
```bash
# Run migrations
heroku run flask db upgrade

# Access database shell
heroku pg:psql

# View connection info
heroku pg:credentials:url

# Create backup
heroku pg:backups:capture

# Download backup
heroku pg:backups:download

# Restore from backup
heroku pg:backups:restore

# View slow queries
heroku pg:diagnose

# Reset database (WARNING: Deletes all data!)
heroku pg:reset DATABASE
```

### Run Commands
```bash
# Run one-off command
heroku run python

# Run Flask CLI command
heroku run flask shell

# Test SMS
heroku run flask test-sms

# Open remote shell
heroku run bash
```

## 🧪 Testing Commands

### Unit Tests
```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov=services --cov-report=html

# Specific test file
pytest tests/test_routes.py -v

# Specific test
pytest tests/test_routes.py::test_signup_successful_submission -v

# Stop on first failure
pytest tests/ -x

# Run in parallel
pytest tests/ -n auto
```

### Load Testing
```bash
# Start Locust web interface
locust -f tests/load_test.py --host=http://localhost:5000

# Headless mode
locust -f tests/load_test.py \
  --headless \
  --users 1000 \
  --spawn-rate 100 \
  --run-time 5m \
  --host=https://your-app.herokuapp.com \
  --html=report.html

# Test production
locust -f tests/load_test.py --host=https://your-app.herokuapp.com
```

### Database Testing
```bash
# Create test database
createdb test_db

# Run migrations on test database
DATABASE_URL=postgresql://localhost/test_db flask db upgrade

# Run tests with specific database
DATABASE_URL=postgresql://localhost/test_db pytest tests/
```

## 🔍 Debugging Commands

### Flask Shell
```bash
# Local
flask shell

# Heroku
heroku run flask shell

# Example commands in shell:
>>> from app import db, Signup
>>> Signup.query.count()
>>> Signup.query.all()
```

### Database Queries
```bash
# Local PostgreSQL
psql signup_db

# Heroku PostgreSQL
heroku pg:psql

# Run SQL query
heroku pg:psql -c "SELECT COUNT(*) FROM signups;"
```

### Redis Debugging
```bash
# Local Redis
redis-cli

# Heroku Redis
heroku redis:cli

# Example commands:
> KEYS *
> GET key_name
> INFO
```

### Check Services
```bash
# Check if Redis is running
redis-cli ping

# Check PostgreSQL
psql -l

# Check Python version
python --version

# Check installed packages
pip list

# Check for security vulnerabilities
pip install safety
safety check
```

## 🛠️ Maintenance Commands

### Update Dependencies
```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade flask

# Check outdated packages
pip list --outdated

# Generate new requirements
pip freeze > requirements.txt
```

### Database Migrations
```bash
# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback one migration
flask db downgrade

# View migration history
flask db history

# View current version
flask db current
```

### Code Quality
```bash
# Format code
black app.py services/ tests/

# Sort imports
isort app.py services/ tests/

# Lint code
flake8 app.py services/ tests/ --max-line-length=120

# Type checking (if using mypy)
mypy app.py services/
```

### Security Checks
```bash
# Check for vulnerable packages
safety check

# Security audit
bandit -r app.py services/ -f json

# Check for secrets in code
pip install detect-secrets
detect-secrets scan
```

## 📊 Monitoring Commands

### Application Metrics
```bash
# Local metrics endpoint
curl http://localhost:5000/metrics

# Production metrics
curl https://your-app.herokuapp.com/metrics

# Health check
curl https://your-app.herokuapp.com/health
```

### Heroku Metrics
```bash
# Web metrics
heroku metrics --web

# PostgreSQL metrics
heroku pg:info

# Redis metrics
heroku redis:info

# View scaling history
heroku releases

# View cost
heroku ps:cost
```

## 🔒 Security Commands

### Generate Secrets
```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Generate random password
python -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32)))"
```

### SSL/HTTPS
```bash
# Force HTTPS in production
heroku config:set FORCE_HTTPS=true

# View SSL info
heroku certs

# Add custom domain
heroku domains:add yourdomain.com
```

## 🚨 Emergency Commands

### Quick Restart
```bash
heroku restart
```

### Rollback Bad Deploy
```bash
heroku rollback
```

### Scale Down (Reduce Costs)
```bash
heroku ps:scale web=1 worker=0
```

### Stop App Temporarily
```bash
heroku ps:scale web=0 worker=0
```

### View Recent Errors
```bash
heroku logs --tail | grep ERROR
```

### Database Connection Issues
```bash
# Reset connections
heroku pg:killall

# Restart database
heroku pg:restart
```

## 📖 Help Commands

```bash
# Heroku help
heroku help
heroku help logs
heroku help ps:scale

# Flask help
flask --help
flask routes  # View all routes

# Git help
git help
git help commit

# pytest help
pytest --help

# Docker help
docker-compose help
docker help
```

## 💡 Useful Aliases (Optional)

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Heroku shortcuts
alias h='heroku'
alias hl='heroku logs --tail'
alias hp='heroku ps'
alias ho='heroku open'
alias hr='heroku restart'

# Git shortcuts
alias gs='git status'
alias ga='git add'
alias gc='git commit -m'
alias gp='git push'
alias gl='git log --oneline'

# Docker shortcuts
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'

# Python/Flask shortcuts
alias fr='flask run'
alias fs='flask shell'
alias pt='pytest tests/ -v'
```

Reload your shell: `source ~/.bashrc` or `source ~/.zshrc`

---

**Tip**: Use `history | grep command` to find commands you've run before!

