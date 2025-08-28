from pydantic import BaseModel
from datetime import datetime

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    post_id: int
    author_id: int

class Comment(CommentBase):
    id: int
    post_id: int
    author_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True