from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import requests

app = FastAPI(title="Post Service", version="1.0.0")

# Configuration
USER_SERVICE_URL = "http://127.0.0.1:8001"

# In-memory storage
posts_db = []
post_id_counter = 1

# Models
class PostCreate(BaseModel):
    title: str
    content: str
    author_id: int

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class Post(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: str

def verify_user_exists(user_id: int):
    """Verify user exists in user service"""
    try:
        response = requests.get(f"{USER_SERVICE_URL}/api/v1/users/{user_id}")
        return response.status_code == 200
    except:
        return False

@app.get("/")
def root():
    return {"message": "Post Service is running!", "service": "post-service"}

@app.post("/api/v1/posts", response_model=Post)
def create_post(post: PostCreate):
    global post_id_counter
    
    # Verify user exists
    if not verify_user_exists(post.author_id):
        raise HTTPException(status_code=400, detail="Author not found")
    
    new_post = {
        "id": post_id_counter,
        "title": post.title,
        "content": post.content,
        "author_id": post.author_id,
        "created_at": datetime.now().isoformat()
    }
    
    posts_db.append(new_post)
    post_id_counter += 1
    
    return new_post

@app.get("/api/v1/posts", response_model=List[Post])
def get_posts():
    return posts_db

@app.get("/api/v1/posts/{post_id}", response_model=Post)
def get_post(post_id: int):
    for post in posts_db:
        if post["id"] == post_id:
            return post
    raise HTTPException(status_code=404, detail="Post not found")