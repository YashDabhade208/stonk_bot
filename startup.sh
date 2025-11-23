#!/bin/bash

# Set environment variables
export PYTHONPATH="$PWD:$PYTHONPATH"

# Activate virtual environment (uncomment if you're using one)
# source venv/bin/activate  # For Linux/Mac
# .\venv\Scripts\activate  # For Windows

# Install dependencies if needed
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs

# Start the FastAPI server with auto-reload
echo "Starting FastAPI server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info
