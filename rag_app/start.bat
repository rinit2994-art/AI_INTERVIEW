@echo off
REM AI Knowledge RAG System Startup Script for Windows

echo Starting AI Knowledge RAG System...
echo.

REM Check if .env exists
if not exist .env (
    echo .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env and add your GEMINI_API_KEY
    echo   Get your key from: https://makersuite.google.com/app/apikey
    echo.
    pause
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create directories
echo Creating directories...
if not exist vector_db\chroma_data mkdir vector_db\chroma_data
if not exist data mkdir data

echo.
echo Setup complete!
echo.
echo Starting server at http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
