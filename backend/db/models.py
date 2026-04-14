"""Database models for the AI Mock Interview System."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    interviews = relationship("Interview", back_populates="user")


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(100), nullable=False)
    experience_level = Column(String(50), nullable=False)
    interview_type = Column(String(50), nullable=False)  # Technical / HR / Mixed
    score = Column(Float, nullable=True)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="interviews")
    answers = relationship("Answer", back_populates="interview")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    question = Column(Text, nullable=False)
    transcript_text = Column(Text, nullable=True)
    evaluation_score = Column(Float, nullable=True)
    technical_accuracy = Column(Float, nullable=True)
    clarity = Column(Float, nullable=True)
    completeness = Column(Float, nullable=True)
    communication = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)

    interview = relationship("Interview", back_populates="answers")
