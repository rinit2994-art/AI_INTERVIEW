#!/bin/bash

# AI Knowledge RAG System Startup Script

set -e

echo "🚀 Starting AI Knowledge RAG System..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "❗ IMPORTANT: Edit .env and add your GEMINI_API_KEY"
    echo "   Get your key from: https://makersuite.google.com/app/apikey"
    echo ""
    read -p "Press Enter after adding your API key..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p vector_db/chroma_data data

# Check if GEMINI_API_KEY is set
source .env
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY not set in .env file!"
    echo "   Please add your Gemini API key to the .env file"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting server at http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
