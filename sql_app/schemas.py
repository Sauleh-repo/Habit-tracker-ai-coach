# sql_app/schemas.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# --- Habit Schemas ---

class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None

class HabitCreate(HabitBase):
    pass

# --- ADD THIS NEW SCHEMA ---
# Defines the fields that can be updated. Both are optional.
class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Habit(HabitBase):
    id: int
    owner_id: int
    last_completed_at: Optional[date] = None

    class Config:
        from_attributes = True

# --- User Schemas ---

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    habits: List[Habit] = []

    class Config:
        from_attributes = True

# --- Token Schemas ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None