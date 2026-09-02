# backend/app/models/message.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)

    role = Column(String(50), nullable=False)          # "user" or "assistant"
    content = Column(Text, nullable=False)
    
    # Optional: keep these if you still want them
    code = Column(Text, nullable=True)
    question = Column(Text, nullable=True)
    answer = Column(Text, nullable=True)
    task = Column(String(50), nullable=True)
    sources = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    conversation = relationship("Conversation", back_populates="messages")