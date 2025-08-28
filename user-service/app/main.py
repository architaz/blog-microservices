from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, database
from .database import engine, get_db
from pydantic import BaseModel
from datetime import datetime
import os

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Service", version="1.0.0")

# Pydantic models
class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    bio: str = ""

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

@app.get("/")
def root():
    return {"message": "User Service is running!", "service": "user-service"}

@app.get("/health")
def health_check():
    return {"service": "user-service", "status": "healthy"}

@app.post("/api/v1/users", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(models.User).filter(
        (models.User.username == user.username) | (models.User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/v1/users", response_model=List[User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/api/v1/users/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user