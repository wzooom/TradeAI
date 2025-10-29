#!/bin/bash

# Fantasy Football Trade Analyzer - Frontend Startup Script

echo "🚀 Starting Fantasy Trade Analyzer Frontend..."

# Navigate to frontend directory
cd fantasy-trade-app

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

echo "🌐 Starting React development server..."
echo "📱 App will be available at http://localhost:3000"

# Start the React development server
npm start
