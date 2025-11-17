#!/bin/bash

###############################################################################
# View Application Logs
# Easy way to monitor your Flask application logs in real-time
###############################################################################

cd "$(dirname "$0")/.."

echo "=========================================="
echo "KC FIFA Signup - Application Logs"
echo "=========================================="
echo ""
echo "Viewing logs in real-time (Press Ctrl+C to stop)"
echo ""

# Check if log file exists
if [ -f flask.log ]; then
    tail -f flask.log
else
    echo "No log file found yet. Starting to monitor..."
    touch flask.log
    tail -f flask.log
fi

