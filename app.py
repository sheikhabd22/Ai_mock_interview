"""
AI Voice-Based Mock Interview System - Main Application
"""
import os
import uuid
import json
from pathlib import Path
from typing import List

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

from backend.db.database import engine, get_db, Base
from backend.db.models import User, Interview, Answer
from backend.schemas.schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    InterviewCreate, InterviewResponse,
    QuestionGenerateRequest, QuestionResponse,
    EvaluateRequest, EvaluationResult, AnswerResponse,
    FinalReport,
)
from backend.api.auth_utils import hash_password, verify_password, create_access_token
from backend.api.dependencies import get_dummy_user
from backend.services.llm_engine import llm_engine
from backend.services.speech_service import stt_service
from backend.services.resume_parser import parse_resume, save_uploaded_resume
from backend.api import interview
from backend.api import auth_routes
from backend.api import generate_questions
from backend.api import upload_audio
from backend.api import evaluation
from backend.api import report
from backend.api import upload_resume
from fastapi.staticfiles import StaticFiles
from backend.core.config import FRONTEND_BUILD_DIR

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="AI Voice-Based Mock Interview System",
    description="An AI-powered mock interview platform with voice interaction",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","https://ai-mock-interview-1-fdnl.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



if FRONTEND_BUILD_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_BUILD_DIR / "static")), name="static")


# ──────────────────────────────────────────────
# Frontend route (serves React build in production)
# ──────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the React app index.html (production build)."""
    index_path = FRONTEND_BUILD_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Frontend not built. Run 'npm run build' in frontend/</h1>")


# ──────────────────────────────────────────────
# Auth endpoints
# ──────────────────────────────────────────────
app.include_router(auth_routes.router, prefix="/api")

app.include_router(upload_resume.router, prefix="/api")
# ──────────────────────────────────────────────
# Interview endpoints
# ──────────────────────────────────────────────
app.include_router(interview.router, prefix="/api")
# ──────────────────────────────────────────────
# Question Generation
# ──────────────────────────────────────────────
app.include_router(generate_questions.router, prefix="/api")

# ──────────────────────────────────────────────
# Audio Upload & Transcription & Resume
# ──────────────────────────────────────────────
app.include_router(upload_audio.router, prefix="/api")

# ──────────────────────────────────────────────
# Answer Evaluation
# ──────────────────────────────────────────────
app.include_router(evaluation.router, prefix="/api")

# ──────────────────────────────────────────────
# Final Report
# ──────────────────────────────────────────────
app.include_router(report.router, prefix="/api")

# ──────────────────────────────────────────────
# Text-to-Speech
# ──────────────────────────────────────────────
from backend.services.tts_service import router as tts_router
app.include_router(tts_router, prefix="/api")


# ──────────────────────────────────────────────
# Health Check
# ──────────────────────────────────────────────
@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "AI Voice Mock Interview System is running"}
