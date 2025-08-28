from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="User Service", version="1.0.0")

# Simple in-memory storage (no database needed)
users_db = []
user_id_counter = 1

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    bio: Optional[str] = ""

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None

class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    bio: str
    created_at: str

@app.get("/")
def root():
    return {"message": "User Service is running!", "service": "user-service"}

@app.get("/health")
def health_check():
    return {"service": "user-service", "status": "healthy"}

@app.post("/api/v1/users", response_model=User)
def create_user(user: UserCreate):
    global user_id_counter
    
    # Check if username or email already exists
    for existing_user in users_db:
        if existing_user["username"] == user.username:
            raise HTTPException(status_code=400, detail="Username already exists")
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = {
        "id": user_id_counter,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "bio": user.bio,
        "created_at": datetime.now().isoformat()
    }
    
    users_db.append(new_user)
    user_id_counter += 1
    
    return new_user

@app.get("/api/v1/users", response_model=List[User])
def get_users(skip: int = 0, limit: int = 100):
    return users_db[skip:skip + limit]

@app.get("/api/v1/users/{user_id}", response_model=User)
def get_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@app.put("/api/v1/users/{user_id}", response_model=User)
def update_user(user_id: int, user_update: UserUpdate):
    for user in users_db:
        if user["id"] == user_id:
            if user_update.full_name is not None:
                user["full_name"] = user_update.full_name
            if user_update.bio is not None:
                user["bio"] = user_update.bio
            return user
    raise HTTPException(status_code=404, detail="User not found")