from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None

class HabitCreate(HabitBase):
    pass

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Habit(HabitBase):
    id: int
    owner_id: int
    last_completed_at: Optional[date] = None

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    habits: List[Habit] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True