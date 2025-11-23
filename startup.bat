@echo off

:: Set environment variables
set PYTHONPATH=%CD%;%PYTHONPATH%

:: Activate virtual environment (uncomment if you're using one)
:: call .\venv\Scripts\activate

:: Install dependencies if needed
pip install -r requirements.txt

:: Create necessary directories
if not exist "logs" mkdir logs

:: Start the FastAPI server with auto-reload
echo Starting FastAPI server...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info

:: Keep the window open after execution
pause
