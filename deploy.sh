#!/bin/bash

# HackRx 6.0 - Deployment Script
echo "🚀 HackRx 6.0 Deployment Script"
echo "================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Build Docker image
echo "📦 Building Docker image..."
docker build -t hackrx-solution .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
else
    echo "❌ Docker build failed!"
    exit 1
fi

# Run container
echo "🔄 Starting container..."
docker run -d \
    --name hackrx-container \
    -p 8000:8000 \
    -e GEMINI_API_KEY="${GEMINI_API_KEY}" \
    -e EMBEDDING_MODEL="all-MiniLM-L6-v2" \
    hackrx-solution

if [ $? -eq 0 ]; then
    echo "✅ Container started successfully!"
    echo "🌐 API is available at: http://localhost:8000"
    echo "📖 API Documentation: http://localhost:8000/docs"
    echo "🔗 Main Endpoint: http://localhost:8000/api/v1/hackrx/run"
else
    echo "❌ Failed to start container!"
    exit 1
fi

echo ""
echo "📋 Container Management Commands:"
echo "  Stop:    docker stop hackrx-container"
echo "  Start:   docker start hackrx-container"
echo "  Remove:  docker rm -f hackrx-container"
echo "  Logs:    docker logs hackrx-container"
