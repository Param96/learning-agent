import sys
import os

# Ensure the 'backend' directory is in the Python path so 'app.*' imports work from the root directory (e.g. on Vercel)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import engine, get_db, Base
from app.routes import goals, plans, activity, plan_revisions, simulate
from app.core.config import get_settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Learning Agent API",
    description="AI-Powered Personal Learning Agent Backend",
    version="0.1.0"
)

settings = get_settings()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "app": "Learning Agent API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Include routers
app.include_router(goals.router)
app.include_router(plans.router)
app.include_router(activity.router)
app.include_router(plan_revisions.router)
app.include_router(simulate.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)