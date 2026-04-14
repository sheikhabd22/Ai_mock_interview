
from fastapi import Depends
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.models import User


def get_dummy_user(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == "dummy@example.com").first()
    
    if not user:
        user = User(name="Dummy User", email="dummy@example.com", password="dummy")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user