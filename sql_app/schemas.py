### sql_app/schemas.py ###

from pydantic import BaseModel
from typing import List, Optional

# --- Habit Schemas ---

class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None

class HabitCreate(HabitBase):
    pass

class Habit(HabitBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

# --- User Schemas ---

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    habits: List[Habit] = []

    class Config:
        orm_mode = True

# --- Token Schemas ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None