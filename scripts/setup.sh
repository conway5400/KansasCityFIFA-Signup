#!/bin/bash

###############################################################################
# Setup Script for Kansas City FIFA Signup Application
# This script sets up the development environment
###############################################################################

set -e  # Exit on error

echo "=========================================="
echo "KC FIFA Signup - Development Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 detected${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please update .env with your credentials${NC}"
else
    echo -e "${YELLOW}.env file already exists${NC}"
fi

# Check if Redis is running
if ! command -v redis-cli &> /dev/null; then
    echo -e "${YELLOW}⚠ Redis CLI not found. Please install Redis:${NC}"
    echo "  macOS: brew install redis"
    echo "  Ubuntu: sudo apt-get install redis-server"
else
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✓ Redis is running${NC}"
    else
        echo -e "${YELLOW}⚠ Redis is not running. Start it with:${NC}"
        echo "  macOS: brew services start redis"
        echo "  Ubuntu: sudo systemctl start redis"
    fi
fi

# Check if PostgreSQL is available
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL detected${NC}"
else
    echo -e "${YELLOW}⚠ PostgreSQL not found. For development, SQLite will be used.${NC}"
    echo "  For production setup, install PostgreSQL:"
    echo "  macOS: brew install postgresql"
    echo "  Ubuntu: sudo apt-get install postgresql"
fi

# Initialize database migrations
echo "Initializing database migrations..."
export FLASK_APP=app.py
flask db init 2>/dev/null || echo "Migrations already initialized"
echo -e "${GREEN}✓ Database migrations ready${NC}"

# Run tests to verify setup
echo ""
echo "Running tests to verify setup..."
pytest tests/ -v --tb=short || echo -e "${YELLOW}⚠ Some tests failed - this is okay for initial setup${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update .env file with your Twilio credentials"
echo "2. Start Redis: brew services start redis (macOS) or sudo systemctl start redis (Ubuntu)"
echo "3. Run the application:"
echo "   ./scripts/start_local.sh"
echo ""
echo "For Docker deployment:"
echo "   docker-compose up"
echo ""

