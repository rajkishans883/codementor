# backend/app/models/message.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)

    code = Column(Text, nullable=True)           # User's code
    question = Column(Text, nullable=False)      # User's question
    answer = Column(Text, nullable=False)        # AI's answer
    task = Column(String(50), default="general") # general / review / explain / optimize
    sources = Column(Text, nullable=True)        # Retrieved sources from RAG

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    conversation = relationship("Conversation", back_populates="messages")