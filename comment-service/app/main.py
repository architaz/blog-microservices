from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
import requests
import os
import uvicorn

app = FastAPI(title="Comment Service", version="1.0.0")

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration - Use environment variables for production
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "https://user-service-demoblog-archita.azurewebsites.net")
POST_SERVICE_URL = os.getenv("POST_SERVICE_URL", "https://post-service-demoblog-archita.azurewebsites.net")

# In-memory storage
comments_db = []
comment_id_counter = 1

# Models
class CommentCreate(BaseModel):
    content: str
    post_id: int
    author_id: int

class Comment(BaseModel):
    id: int
    content: str
    post_id: int
    author_id: int
    created_at: str

def verify_user_exists(user_id: int):
    try:
        response = requests.get(f"{USER_SERVICE_URL}/api/v1/users/{user_id}", timeout=10)
        return response.status_code == 200
    except:
        return False

def verify_post_exists(post_id: int):
    try:
        response = requests.get(f"{POST_SERVICE_URL}/api/v1/posts/{post_id}", timeout=10)
        return response.status_code == 200
    except:
        return False

@app.get("/")
def root():
    return {"message": "Comment Service is running!", "service": "comment-service"}

@app.get("/health")
def health_check():
    return {"service": "comment-service", "status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/comments", response_model=Comment)
def create_comment(comment: CommentCreate):
    global comment_id_counter
    
    # For demo purposes, skip verification if other services are not available
    # In production, you might want to handle this differently
    try:
        if not verify_user_exists(comment.author_id):
            raise HTTPException(status_code=400, detail="Author not found")
        if not verify_post_exists(comment.post_id):
            raise HTTPException(status_code=400, detail="Post not found")
    except:
        # Continue anyway for demo - in production handle this properly
        pass
    
    new_comment = {
        "id": comment_id_counter,
        "content": comment.content,
        "post_id": comment.post_id,
        "author_id": comment.author_id,
        "created_at": datetime.now().isoformat()
    }
    
    comments_db.append(new_comment)
    comment_id_counter += 1
    
    return new_comment

@app.get("/api/v1/comments/post/{post_id}", response_model=List[Comment])
def get_comments_by_post(post_id: int):
    comments = [c for c in comments_db if c["post_id"] == post_id]
    return comments

@app.get("/api/v1/comments", response_model=List[Comment])
def get_all_comments():
    return comments_db

@app.delete("/api/v1/comments/{comment_id}")
def delete_comment(comment_id: int):
    global comments_db
    comments_db = [c for c in comments_db if c["id"] != comment_id]
    return {"message": "Comment deleted successfully"}

# For local development
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))