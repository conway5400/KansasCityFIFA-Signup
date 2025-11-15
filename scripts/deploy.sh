#!/bin/bash

###############################################################################
# Deployment Script for Heroku
# Deploys the application to Heroku with proper configuration
###############################################################################

set -e

echo "=========================================="
echo "KC FIFA Signup - Heroku Deployment"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo -e "${RED}Error: Heroku CLI is not installed${NC}"
    echo "Install from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi
echo -e "${GREEN}✓ Heroku CLI detected${NC}"

# Check if logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo -e "${YELLOW}Not logged in to Heroku. Logging in...${NC}"
    heroku login
fi
echo -e "${GREEN}✓ Logged in to Heroku${NC}"

# Get app name
read -p "Enter Heroku app name (or press Enter to create new app): " APP_NAME

if [ -z "$APP_NAME" ]; then
    echo "Creating new Heroku app..."
    APP_NAME=$(heroku create --json | python3 -c "import sys, json; print(json.load(sys.stdin)['name'])")
    echo -e "${GREEN}✓ Created app: $APP_NAME${NC}"
else
    # Check if app exists
    if ! heroku apps:info --app $APP_NAME &> /dev/null; then
        echo "App doesn't exist. Creating..."
        heroku create $APP_NAME
        echo -e "${GREEN}✓ Created app: $APP_NAME${NC}"
    else
        echo -e "${GREEN}✓ Using existing app: $APP_NAME${NC}"
    fi
fi

# Add git remote if it doesn't exist
if ! git remote get-url heroku &> /dev/null; then
    git remote add heroku https://git.heroku.com/$APP_NAME.git
    echo -e "${GREEN}✓ Added Heroku git remote${NC}"
fi

# Add required add-ons
echo ""
echo "Configuring Heroku add-ons..."

# PostgreSQL
if ! heroku addons:info heroku-postgresql --app $APP_NAME &> /dev/null; then
    echo "Adding PostgreSQL..."
    heroku addons:create heroku-postgresql:mini --app $APP_NAME
    echo -e "${GREEN}✓ PostgreSQL added${NC}"
else
    echo -e "${GREEN}✓ PostgreSQL already configured${NC}"
fi

# Redis
if ! heroku addons:info heroku-redis --app $APP_NAME &> /dev/null; then
    echo "Adding Redis..."
    heroku addons:create heroku-redis:mini --app $APP_NAME
    echo -e "${GREEN}✓ Redis added${NC}"
else
    echo -e "${GREEN}✓ Redis already configured${NC}"
fi

# Configure environment variables
echo ""
echo "Configuring environment variables..."

# Check if .env file exists
if [ -f ".env" ]; then
    # Parse .env and set config vars (skip comments and empty lines)
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ $key =~ ^#.*$ ]] && continue
        [[ -z $key ]] && continue
        
        # Remove quotes from value
        value="${value%\"}"
        value="${value#\"}"
        
        # Set config var
        if [ ! -z "$value" ] && [ "$key" != "DATABASE_URL" ]; then
            heroku config:set "$key=$value" --app $APP_NAME
        fi
    done < .env
    echo -e "${GREEN}✓ Environment variables configured${NC}"
else
    echo -e "${YELLOW}⚠ .env file not found. Manual configuration required:${NC}"
    echo "  heroku config:set SECRET_KEY=your-secret-key --app $APP_NAME"
    echo "  heroku config:set TWILIO_ACCOUNT_SID=your-sid --app $APP_NAME"
    echo "  heroku config:set TWILIO_AUTH_TOKEN=your-token --app $APP_NAME"
    echo "  heroku config:set TWILIO_FROM_NUMBER=your-number --app $APP_NAME"
fi

# Set Flask environment to production
heroku config:set FLASK_ENV=production --app $APP_NAME

# Configure buildpacks
echo ""
echo "Configuring buildpacks..."
heroku buildpacks:set heroku/python --app $APP_NAME
echo -e "${GREEN}✓ Buildpacks configured${NC}"

# Scale dynos
echo ""
echo "Configuring dynos..."
heroku ps:scale web=1 worker=1 --app $APP_NAME
echo -e "${GREEN}✓ Dynos configured (1 web, 1 worker)${NC}"

# Deploy
echo ""
echo "Deploying to Heroku..."
git push heroku main || git push heroku master

# Run database migrations
echo ""
echo "Running database migrations..."
heroku run flask db upgrade --app $APP_NAME || echo -e "${YELLOW}⚠ Migrations may need to be run manually${NC}"

# Open the app
echo ""
echo "=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "App URL: https://$APP_NAME.herokuapp.com"
echo ""
echo "Useful commands:"
echo "  View logs:        heroku logs --tail --app $APP_NAME"
echo "  Run migrations:   heroku run flask db upgrade --app $APP_NAME"
echo "  Scale workers:    heroku ps:scale worker=2 --app $APP_NAME"
echo "  Open app:         heroku open --app $APP_NAME"
echo ""

# Ask if user wants to open the app
read -p "Open app in browser? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    heroku open --app $APP_NAME
fi

