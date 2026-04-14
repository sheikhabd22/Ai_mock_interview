from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.db.database import get_db
from backend.db.models import Interview, User
from backend.schemas.schemas import InterviewCreate, InterviewResponse
from backend.api.dependencies import get_dummy_user  
from backend.services.llm_engine import llm_engine
from backend.schemas.schemas import QuestionGenerateRequest, QuestionResponse
from backend.services.resume_parser import parse_resume, save_uploaded_resume
from fastapi import UploadFile, File
from pathlib import Path

router = APIRouter(tags=["Upload Resume"])

@router.post("/upload-resume")
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
