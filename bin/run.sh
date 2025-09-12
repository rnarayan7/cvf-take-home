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

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Please run this script from the src/ directory"
    echo "   cd src && ./run.sh"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ] && [ ! -f ".requirements_installed" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    touch .requirements_installed
    echo "✅ Dependencies installed"
fi

# Run the Python script with all arguments passed through
echo "🚀 Starting CVF API..."
python3 run.py "$@"