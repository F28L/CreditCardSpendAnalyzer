#!/bin/bash

# Finance AI Frontend Startup Script
# Run this from the frontend directory

echo "🎨 Starting Finance AI Frontend..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Dependencies not installed!"
    echo "📦 Run: npm install"
    exit 1
fi

# Start Vite dev server
echo "✅ Starting server on http://localhost:5173"
npm run dev
