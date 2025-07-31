#!/bin/bash

echo "🚀 HackRx 6.0 - Starting Intelligent Query-Retrieval System"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found"
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit .env file and add your GEMINI_API_KEY"
    echo "Then run this script again"
    exit 1
fi

# Install requirements
echo "📦 Installing requirements..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install requirements"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo "🌐 Starting server at http://localhost:8000"
echo "📖 API docs will be available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 main.py
