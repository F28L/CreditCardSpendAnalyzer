#!/bin/bash

# Finance AI Backend Startup Script
# Run this from the backend directory

echo "🚀 Starting Finance AI Backend..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "📦 Run: poetry install"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "📝 Run: cp .env.example .env"
    exit 1
fi

# Activate poetry environment and run
echo "✅ Starting server on http://localhost:8000"
poetry run python main.py
