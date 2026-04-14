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

from backend.database import engine, get_db, Base
from backend.models import User, Interview, Answer
from backend.schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    InterviewCreate, InterviewResponse,
    QuestionGenerateRequest, QuestionResponse,
    EvaluateRequest, EvaluationResult, AnswerResponse,
    FinalReport,
)
from backend.auth import hash_password, verify_password, create_access_token

def get_dummy_user(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == "dummy@example.com").first()
    if not user:
        user = User(name="Dummy User", email="dummy@example.com", password="dummy")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

from backend.llm_engine import llm_engine
from backend.speech_service import stt_service
from backend.resume_parser import parse_resume, save_uploaded_resume

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files — React build (production) or dev proxy
FRONTEND_BUILD_DIR = Path(__file__).parent / "frontend" / "build"
UPLOAD_DIR = Path(__file__).parent / "backend" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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
@app.post("/api/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/api/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login and receive a JWT token."""
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(data={"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}


# ──────────────────────────────────────────────
# Interview endpoints
# ──────────────────────────────────────────────
@app.post("/api/interviews", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
def create_interview(
    data: InterviewCreate,
    current_user: User = Depends(get_dummy_user),
    db: Session = Depends(get_db),
):
    """Create a new interview session."""
    interview = Interview(
        user_id=current_user.id,
        role=data.role,
        experience_level=data.experience_level,
        interview_type=data.interview_type,
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


@app.get("/api/interviews", response_model=List[InterviewResponse])
def list_interviews(
    current_user: User = Depends(get_dummy_user),
    db: Session = Depends(get_db),
):
    """List all interviews for the current user."""
    return db.query(Interview).filter(Interview.user_id == current_user.id).all()


# ──────────────────────────────────────────────
# Question Generation
# ──────────────────────────────────────────────
@app.post("/api/generate-questions", response_model=QuestionResponse)
def generate_questions(
    data: QuestionGenerateRequest,
    current_user: User = Depends(get_dummy_user),
):
    """Generate interview questions based on role, experience, and type."""
    questions = llm_engine.generate_questions(
        role=data.role,
        experience_level=data.experience_level,
        interview_type=data.interview_type,
        num_questions=data.num_questions,
        resume_text=data.resume_text,
    )
    return {"questions": questions}


# ──────────────────────────────────────────────
# Audio Upload & Transcription & Resume
# ──────────────────────────────────────────────
@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload a resume and extract its text."""
    allowed_extensions = {".pdf", ".docx", ".doc", ".txt"}
    ext = Path(file.filename).suffix.lower() if file.filename else ".pdf"
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported resume format: {ext}")
    
    content = await file.read()
    file_path = save_uploaded_resume(content, file.filename)
    
    try:
        parsed_data = parse_resume(file_path)
        return {"parsed_data": parsed_data, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")

@app.post("/api/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """Upload an audio file and return the saved file path."""
    allowed_extensions = {".wav", ".mp3", ".webm", ".ogg", ".m4a"}
    ext = Path(file.filename).suffix.lower() if file.filename else ".webm"
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported audio format: {ext}")

    filename = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / filename

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return {"filename": filename, "path": str(file_path)}


@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Upload audio and transcribe it to text."""
    ext = Path(file.filename).suffix.lower() if file.filename else ".webm"
    filename = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / filename

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        if ext == ".webm":
            transcript = stt_service.transcribe_from_webm(str(file_path))
        else:
            transcript = stt_service.transcribe_audio(str(file_path))
        return {"transcript": transcript, "filename": filename}
    except Exception as e:
        # Keep interview flow usable even when local audio codecs/services are unavailable.
        return {
            "transcript": "[Transcription unavailable. Please type or retry after configuring ffmpeg/speech service.]",
            "filename": filename,
            "warning": f"Transcription failed: {str(e)}",
        }


# ──────────────────────────────────────────────
# Answer Evaluation
# ──────────────────────────────────────────────
@app.post("/api/evaluate", response_model=EvaluationResult)
def evaluate_answer(
    data: EvaluateRequest,
    current_user: User = Depends(get_dummy_user),
    db: Session = Depends(get_db),
):
    """Evaluate a transcribed answer using the LLM."""
    interview = db.query(Interview).filter(
        Interview.id == data.interview_id,
        Interview.user_id == current_user.id,
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # Get evaluation from LLM
    evaluation = llm_engine.evaluate_answer(
        question=data.question,
        answer=data.transcript_text,
        role=interview.role,
        experience_level=interview.experience_level,
    )

    # Save answer to database
    answer = Answer(
        interview_id=interview.id,
        question=data.question,
        transcript_text=data.transcript_text,
        evaluation_score=evaluation["overall_score"],
        technical_accuracy=evaluation["technical_accuracy"],
        clarity=evaluation["clarity"],
        completeness=evaluation["completeness"],
        communication=evaluation["communication"],
        feedback=json.dumps({
            "strengths": evaluation["strengths"],
            "weaknesses": evaluation["weaknesses"],
            "suggestions": evaluation["suggestions"],
        }),
    )
    db.add(answer)
    db.commit()

    return evaluation


# ──────────────────────────────────────────────
# Final Report
# ──────────────────────────────────────────────
@app.get("/api/final-report/{interview_id}", response_model=FinalReport)
def get_final_report(
    interview_id: int,
    current_user: User = Depends(get_dummy_user),
    db: Session = Depends(get_db),
):
    """Generate a final performance report for an interview."""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id,
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    answers = db.query(Answer).filter(Answer.interview_id == interview_id).all()

    if not answers:
        raise HTTPException(status_code=404, detail="No answers found for this interview")

    # Calculate overall score
    scores = [a.evaluation_score for a in answers if a.evaluation_score is not None]
    overall_score = (sum(scores) / len(scores) * 10) if scores else 0  # Convert to 0-100

    # Update interview score
    interview.score = overall_score
    db.commit()

    # Generate report summary using LLM
    answers_data = [
        {"question": a.question, "evaluation_score": a.evaluation_score}
        for a in answers
    ]
    summary = llm_engine.generate_final_report_summary(answers_data, interview.role)

    return FinalReport(
        interview_id=interview.id,
        role=interview.role,
        experience_level=interview.experience_level,
        interview_type=interview.interview_type,
        overall_score=overall_score,
        total_questions=len(answers),
        answers=answers,
        strengths=summary.get("strengths", []),
        weaknesses=summary.get("weaknesses", []),
        suggestions=summary.get("suggestions", []),
    )


# ──────────────────────────────────────────────
# Health Check
# ──────────────────────────────────────────────
@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "AI Voice Mock Interview System is running"}
