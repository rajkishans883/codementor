# backend/app/models/conversation.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = {"extend_existing": True}   # ← Add this line

    id = Column(Integer, primary_key=True, index=True)
    
    coding_session_id = Column(Integer, ForeignKey("coding_sessions.id", ondelete="CASCADE"), nullable=True, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="conversations")
    coding_session = relationship("CodingSession", back_populates="conversation")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")