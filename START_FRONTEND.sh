#!/bin/bash

# Quick start script for the frontend

echo "🚀 Starting Medical Appointment Scheduler Frontend..."
echo ""

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Check if backend is running
echo "🔍 Checking if backend is running..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "⚠️  Backend is not running on http://localhost:8000"
    echo "   Please start the backend first: python run.py"
    echo ""
fi

echo ""
echo "🎨 Starting frontend development server..."
echo "   Frontend will be available at: http://localhost:3000"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""

# Start the development server
npm run dev

