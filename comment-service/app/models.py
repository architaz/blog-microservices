from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    post_id = Column(Integer, nullable=False)  # Foreign key to post service
    author_id = Column(Integer, nullable=False)  # Foreign key to user service
    created_at = Column(DateTime(timezone=True), server_default=func.now())