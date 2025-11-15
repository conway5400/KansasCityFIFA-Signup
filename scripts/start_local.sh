#!/bin/bash

###############################################################################
# Local Development Startup Script
# Starts all services needed for local development
###############################################################################

set -e

echo "=========================================="
echo "KC FIFA Signup - Starting Local Development"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo "Run ./scripts/setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✓ Environment variables loaded${NC}"
else
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Run ./scripts/setup.sh first"
    exit 1
fi

# Check if Redis is running
if ! redis-cli ping &> /dev/null; then
    echo -e "${RED}Error: Redis is not running${NC}"
    echo "Start Redis with:"
    echo "  macOS: brew services start redis"
    echo "  Ubuntu: sudo systemctl start redis"
    exit 1
fi
echo -e "${GREEN}✓ Redis is running${NC}"

# Run database migrations
echo "Running database migrations..."
export FLASK_APP=app.py
flask db upgrade 2>/dev/null || flask db init && echo "Database migrations applied"

# Create database tables if they don't exist
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('✓ Database tables created')" 2>/dev/null || echo "Database already initialized"

echo ""
echo "=========================================="
echo -e "${GREEN}Starting Services...${NC}"
echo "=========================================="
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $(jobs -p) 2>/dev/null || true
    echo "Services stopped"
}
trap cleanup EXIT

# Start Celery worker in background
echo "Starting Celery worker..."
celery -A app.celery worker --loglevel=info &
CELERY_PID=$!
echo -e "${GREEN}✓ Celery worker started (PID: $CELERY_PID)${NC}"

# Wait a moment for Celery to start
sleep 2

# Start Flask application
echo ""
echo "Starting Flask application..."
echo "=========================================="
echo -e "${GREEN}Application running at: http://localhost:5000${NC}"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Start Flask (this will block)
flask run --host=0.0.0.0 --port=5000 --reload

