#!/bin/bash

# Fantasy Football Trade Analyzer - Backend Startup Script

echo "🚀 Starting Fantasy Trade Analyzer Backend..."

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if model file exists
if [ ! -f "../models/fp_model_final.keras" ]; then
    echo "❌ Error: Model file not found at ../models/fp_model_final.keras"
    echo "Please ensure your trained model is in the correct location."
    exit 1
fi

# Check if data file exists
if [ ! -f "../data/nfl_seasonal_preprocessed.csv" ]; then
    echo "❌ Error: Data file not found at ../data/nfl_seasonal_preprocessed.csv"
    echo "Please ensure your preprocessed data is in the correct location."
    exit 1
fi

echo "✅ All files found. Starting API server..."
echo "🌐 API will be available at http://localhost:8000"
echo "📖 API docs will be available at http://localhost:8000/docs"

# Start the FastAPI server
python main.py
