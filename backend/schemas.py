"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# --- Auth Schemas ---
class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# --- Interview Schemas ---
class InterviewCreate(BaseModel):
    role: str
    experience_level: str
    interview_type: str  # Technical / HR / Mixed


class InterviewResponse(BaseModel):
    id: int
    role: str
    experience_level: str
    interview_type: str
    score: Optional[float] = None
    date: datetime

    class Config:
        from_attributes = True


class QuestionGenerateRequest(BaseModel):
    role: str
    experience_level: str
    interview_type: str
    num_questions: int = 5
    resume_text: Optional[str] = None


class QuestionResponse(BaseModel):
    questions: List[str]


# --- Answer / Evaluation Schemas ---
class EvaluateRequest(BaseModel):
    interview_id: int
    question: str
    transcript_text: str


class EvaluationResult(BaseModel):
    overall_score: float
    technical_accuracy: float
    clarity: float
    completeness: float
    communication: float
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]


class AnswerResponse(BaseModel):
    id: int
    interview_id: int
    question: str
    transcript_text: Optional[str] = None
    evaluation_score: Optional[float] = None
    technical_accuracy: Optional[float] = None
    clarity: Optional[float] = None
    completeness: Optional[float] = None
    communication: Optional[float] = None
    feedback: Optional[str] = None

    class Config:
        from_attributes = True


# --- Report Schema ---
class FinalReport(BaseModel):
    interview_id: int
    role: str
    experience_level: str
    interview_type: str
    overall_score: float
    total_questions: int
    answers: List[AnswerResponse]
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
