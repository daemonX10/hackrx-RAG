@echo off
echo 🚀 HackRx 6.0 Deployment Script
echo =================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    pause
    exit /b 1
)

REM Build Docker image
echo 📦 Building Docker image...
docker build -t hackrx-solution .

if %errorlevel% neq 0 (
    echo ❌ Docker build failed!
    pause
    exit /b 1
)

echo ✅ Docker image built successfully!

REM Stop and remove existing container if it exists
docker stop hackrx-container >nul 2>&1
docker rm hackrx-container >nul 2>&1

REM Run container
echo 🔄 Starting container...
docker run -d --name hackrx-container -p 8000:8000 -e GEMINI_API_KEY=%GEMINI_API_KEY% -e EMBEDDING_MODEL=all-MiniLM-L6-v2 hackrx-solution

if %errorlevel% neq 0 (
    echo ❌ Failed to start container!
    pause
    exit /b 1
)

echo ✅ Container started successfully!
echo 🌐 API is available at: http://localhost:8000
echo 📖 API Documentation: http://localhost:8000/docs
echo 🔗 Main Endpoint: http://localhost:8000/api/v1/hackrx/run
echo.
echo 📋 Container Management Commands:
echo   Stop:    docker stop hackrx-container
echo   Start:   docker start hackrx-container
echo   Remove:  docker rm -f hackrx-container
echo   Logs:    docker logs hackrx-container

pause
