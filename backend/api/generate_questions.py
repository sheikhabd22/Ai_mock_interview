from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.db.database import get_db
from backend.db.models import Interview, User
from backend.schemas.schemas import InterviewCreate, InterviewResponse
from backend.api.auth_utils import get_current_user
from backend.services.llm_engine import llm_engine
from backend.schemas.schemas import QuestionGenerateRequest, QuestionResponse

router = APIRouter(tags=["Generate Questions"])

@router.post("/generate-questions", response_model=QuestionResponse)
def generate_questions(
    data: QuestionGenerateRequest,
    current_user: User = Depends(get_current_user),
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
