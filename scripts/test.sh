#!/bin/bash

###############################################################################
# Test Script
# Runs all tests with coverage reporting
###############################################################################

set -e

echo "=========================================="
echo "KC FIFA Signup - Running Tests"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set test environment
export FLASK_ENV=testing

# Run tests with coverage
echo "Running unit tests with coverage..."
pytest tests/ \
    --verbose \
    --cov=app \
    --cov=services \
    --cov=config \
    --cov-report=term-missing \
    --cov-report=html \
    --tb=short

echo ""
echo -e "${GREEN}✓ Tests complete${NC}"
echo ""
echo "Coverage report generated in htmlcov/index.html"
echo ""

# Optional: Run linting
if command -v flake8 &> /dev/null; then
    echo "Running code quality checks..."
    flake8 app.py config.py services/ --max-line-length=120 --exclude=venv,migrations || echo -e "${YELLOW}⚠ Some linting issues found${NC}"
fi

