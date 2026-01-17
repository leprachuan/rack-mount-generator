#!/bin/bash

# 19" Rack Mount Generator - Startup Script

echo "🔧 19\" Rack Mount Generator - Startup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python version: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check for required files
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found in current directory"
    exit 1
fi

if [ ! -f "index.html" ]; then
    echo "❌ index.html not found in current directory"
    exit 1
fi

if [ ! -f "stl_generator.py" ]; then
    echo "❌ stl_generator.py not found in current directory"
    exit 1
fi

echo "✓ All required files found"
echo ""

# Display startup info
echo "========================================"
echo "🚀 Starting Server..."
echo "========================================"
echo ""
echo "📍 Web Interface: http://localhost:5000"
echo "📝 API Base: http://localhost:5000/api"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the application
python3 app.py
