### sql_app/models.py ###

# 1. Added 'DateTime' to the sqlalchemy imports
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship

# 2. Added standard datetime import for the default timestamp
from datetime import datetime

from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Relationships
    habits = relationship("Habit", back_populates="owner")
    chat_messages = relationship("ChatMessage", back_populates="user")

class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # This stores the date the habit was last marked as complete.
    last_completed_at = Column(Date, nullable=True)

    owner = relationship("User", back_populates="habits")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String)  # 'user' (You) or 'model' (AI)
    content = Column(String)
    
    # This uses the DateTime type imported from sqlalchemy
    # and the datetime.utcnow function for the default value
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_messages")