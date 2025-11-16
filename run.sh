#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create .env file with OPENAI_API_KEY"
    echo "You can copy .env.example and fill in your API key"
    exit 1
fi

# Start FastAPI application
echo "Starting Job Search Helper..."
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

