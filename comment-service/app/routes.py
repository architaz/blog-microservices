from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import requests
import os
from . import models, schemas
from .database import get_db

router = APIRouter()
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")
POST_SERVICE_URL = os.getenv("POST_SERVICE_URL", "http://localhost:8002")

def verify_user_exists(user_id: int):
    try:
        response = requests.get(f"{USER_SERVICE_URL}/api/v1/users/{user_id}")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def verify_post_exists(post_id: int):
    try:
        response = requests.get(f"{POST_SERVICE_URL}/api/v1/posts/{post_id}")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

@router.post("/comments", response_model=schemas.Comment)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    # Verify user and post exist
    if not verify_user_exists(comment.author_id):
        raise HTTPException(status_code=400, detail="Author not found")
    if not verify_post_exists(comment.post_id):
        raise HTTPException(status_code=400, detail="Post not found")
    
    db_comment = models.Comment(**comment.model_dump())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/comments/post/{post_id}", response_model=List[schemas.Comment])
def get_comments_by_post(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).filter(models.Comment.post_id == post_id).all()
    return comments

@router.get("/comments/{comment_id}", response_model=schemas.Comment)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted successfully"}