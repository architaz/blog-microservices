from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import uvicorn

app = FastAPI(title="User Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use in-memory storage instead of database
users_db = []
user_id_counter = 1

# Your existing Pydantic models here...
class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    bio: str = ""

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

# Replace your database-dependent endpoints with in-memory versions
@app.post("/api/v1/users", response_model=User)
def create_user(user: UserCreate):
    global user_id_counter
    
    # Check if user exists
    for existing_user in users_db:
        if existing_user["username"] == user.username or existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Username or email already exists")
    
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

# For Azure deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)