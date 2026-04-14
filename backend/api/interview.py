from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from backend.db.database import get_db
from backend.db.models import Interview, User
from backend.schemas.schemas import InterviewCreate, InterviewResponse
from backend.api.dependencies import get_dummy_user  

router = APIRouter(tags=["Interview"])


@router.post("/interviews", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
def create_interview(
    data: InterviewCreate,
    current_user: User = Depends(get_dummy_user),
    db: Session = Depends(get_db),
):
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


@router.get("/interviews", response_model=List[InterviewResponse])
def list_interviews(
    current_user: User = Depends(get_dummy_user),
    db: Session = Depends(get_db),
):
    return db.query(Interview).filter(Interview.user_id == current_user.id).all()