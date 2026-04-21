from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from backend.db.database import get_db
from backend.db.models import Interview, User, Answer
from backend.schemas.schemas import InterviewCreate, InterviewResponse
from backend.api.auth_utils import get_current_user
from backend.services.llm_engine import llm_engine
from backend.schemas.schemas import QuestionGenerateRequest, QuestionResponse, EvaluateRequest, EvaluationResult

router = APIRouter(tags=["Evaluation"])

@router.post("/evaluate", response_model=EvaluationResult)
def evaluate_answer(
    data: EvaluateRequest,
    current_user: User = Depends(get_current_user),
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
