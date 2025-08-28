from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import requests
import os
from . import models, schemas
from .database import get_db

router = APIRouter()
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")

def verify_user_exists(user_id: int):
    """Verify user exists in user service"""
    try:
        response = requests.get(f"{USER_SERVICE_URL}/api/v1/users/{user_id}")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

@router.post("/posts", response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # Verify user exists
    if not verify_user_exists(post.author_id):
        raise HTTPException(status_code=400, detail="Author not found")
    
    db_post = models.Post(**post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@router.get("/posts", response_model=List[schemas.Post])
def get_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = db.query(models.Post).offset(skip).limit(limit).all()
    return posts

@router.get("/posts/{post_id}", response_model=schemas.Post)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.get("/posts/author/{author_id}", response_model=List[schemas.Post])
def get_posts_by_author(author_id: int, db: Session = Depends(get_db)):
    posts = db.query(models.Post).filter(models.Post.author_id == author_id).all()
    return posts

@router.put("/posts/{post_id}", response_model=schemas.Post)
def update_post(post_id: int, post_update: schemas.PostUpdate, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    for field, value in post_update.model_dump(exclude_unset=True).items():
        setattr(post, field, value)
    
    db.commit()
    db.refresh(post)
    return post

@router.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}