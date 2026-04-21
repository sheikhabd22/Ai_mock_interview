from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.db.database import get_db
from backend.db.models import Interview, User, Answer
from backend.schemas.schemas import InterviewCreate, InterviewResponse
from backend.api.auth_utils import get_current_user
from backend.services.llm_engine import llm_engine
from backend.schemas.schemas import QuestionGenerateRequest, QuestionResponse, EvaluateRequest, EvaluationResult, FinalReport    

router = APIRouter(tags=["Report"])

@router.get("/final-report/{interview_id}", response_model=FinalReport)
def get_final_report(
    interview_id: int,
    current_user: User = Depends(get_current_user),
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