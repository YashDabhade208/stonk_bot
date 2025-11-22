from fastapi import FastAPI
from datetime import datetime
from app.core.db_config import test_db_connection

app = FastAPI(
    title="Stock Trading Bot API",
    description="Backend API for AI-powered stock news, insights, and paper trading.",
    version="0.1.0",
)

@app.on_event("startup")
def startup_event():
    test_db_connection()
