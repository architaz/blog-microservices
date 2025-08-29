from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import requests
import os
import uvicorn

app = FastAPI(title="Post Service", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration - Use environment variables
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "https://user-service-demoblog-archita.azurewebsites.net")

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
    try:
        response = requests.get(f"{USER_SERVICE_URL}/api/v1/users/{user_id}", timeout=10)
        return response.status_code == 200
    except:
        return False

@app.get("/")
def root():
    return {"message": "Post Service is running!", "service": "post-service"}

@app.get("/health")
def health_check():
    return {"service": "post-service", "status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/posts", response_model=Post)
def create_post(post: PostCreate):
    global post_id_counter
    
    # For demo purposes, skip verification if user service is not available
    try:
        if not verify_user_exists(post.author_id):
            raise HTTPException(status_code=400, detail="Author not found")
    except:
        pass
    
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

@app.put("/api/v1/posts/{post_id}", response_model=Post)
def update_post(post_id: int, post_update: PostUpdate):
    for post in posts_db:
        if post["id"] == post_id:
            if post_update.title is not None:
                post["title"] = post_update.title
            if post_update.content is not None:
                post["content"] = post_update.content
            return post
    raise HTTPException(status_code=404, detail="Post not found")

@app.delete("/api/v1/posts/{post_id}")
def delete_post(post_id: int):
    global posts_db
    posts_db = [p for p in posts_db if p["id"] != post_id]
    return {"message": "Post deleted successfully"}

# For Azure deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)