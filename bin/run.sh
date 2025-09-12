#!/bin/bash

# CVF Portfolio Management API - Quick Start Script

set -e  # Exit on any error

echo "======================================================"
echo "CVF Portfolio Management API - Quick Start"
echo "======================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Run the Python script with all arguments passed through
echo "🚀 Starting CVF API..."
PYTHONPATH=. python3 src/python/cli.py "$@"