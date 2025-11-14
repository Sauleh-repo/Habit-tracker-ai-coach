### sql_app/models.py ###

# Add 'Date' to this import from sqlalchemy
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    habits = relationship("Habit", back_populates="owner")

class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # --- ADD THIS NEW COLUMN ---
    # This will store the date the habit was last marked as complete.
    last_completed_at = Column(Date, nullable=True)

    owner = relationship("User", back_populates="habits")