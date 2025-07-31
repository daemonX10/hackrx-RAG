@echo off
echo 🚀 HackRx 6.0 - Starting Intelligent Query-Retrieval System
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found
    echo Copying .env.example to .env...
    copy .env.example .env
    echo.
    echo 📝 Please edit .env file and add your GEMINI_API_KEY
    echo Then run this script again
    pause
    exit /b 1
)

REM Install requirements
echo 📦 Installing requirements...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)

echo.
echo ✅ Setup complete!
echo 🌐 Starting server at http://localhost:8000
echo 📖 API docs will be available at http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python main.py
