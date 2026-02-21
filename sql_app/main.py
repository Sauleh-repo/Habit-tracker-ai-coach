import os
from datetime import timedelta, date
from typing import List, Optional
from contextlib import asynccontextmanager

# NEW SDK IMPORT
from google import genai
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from pydantic import BaseModel

from . import crud, models, schemas, security
from .database import SessionLocal, engine

# 1. Configuration & Global State
load_dotenv()

class AIState:
    client: Optional[genai.Client] = None

ai_state = AIState()

# 2. Lifespan: Prevents server hang and auto-creates database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            ai_state.client = genai.Client(api_key=api_key)
            print("Gemini AI Client initialized successfully.")

            print("DEBUG: about to list models")

            for m in ai_state.client.models.list():
                print("MODEL FOUND:", m.name)

            print("DEBUG: model listing finished")



        except Exception as e:
            print(f"Failed to initialize Gemini Client: {e}")
    else:
        print("Warning: GOOGLE_API_KEY not found.")

    yield
    ai_state.client = None


app = FastAPI(lifespan=lifespan)

# 3. CORS Configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://34.54.156.38", # Your GCP IP
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

# 5. User Endpoints
@app.post("/users/register", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

# 6. Habit Endpoints
@app.post("/habits/", response_model=schemas.Habit)
def create_habit_for_user(habit: schemas.HabitCreate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.create_user_habit(db=db, habit=habit, user_id=current_user.id)

@app.get("/habits/", response_model=List[schemas.Habit])
def read_habits(current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Habit).filter(models.Habit.owner_id == current_user.id).all()

@app.put("/habits/{habit_id}/toggle", response_model=schemas.Habit)
def toggle_habit_completion(habit_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
    if not habit or habit.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    today = date.today()
    habit.last_completed_at = None if habit.last_completed_at == today else today
    db.commit()
    db.refresh(habit)
    return habit

@app.put("/habits/{habit_id}", response_model=schemas.Habit)
def update_habit_details(habit_id: int, habit_update: schemas.HabitUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
    if not habit or habit.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found")
    return crud.update_habit(db=db, habit_id=habit_id, habit_update=habit_update)

@app.delete("/habits/{habit_id}")
def delete_habit(habit_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
    if not habit or habit.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found")
    return crud.delete_habit(db=db, habit_id=habit_id)

# 7. AI Chatbot Endpoint
class ChatbotResponse(BaseModel):
    reply: str

@app.post("/chatbot/analyze", response_model=ChatbotResponse)
async def analyze_habits(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not ai_state.client:
        raise HTTPException(status_code=503, detail="AI service is not configured.")

    habits = db.query(models.Habit).filter(models.Habit.owner_id == current_user.id).all()
    if not habits:
        return ChatbotResponse(reply="You haven't added any habits yet. Add some first!")

    today = date.today()
    habit_list_str = "\n".join([
        f"- {h.name}: {'Completed today' if h.last_completed_at == today else 'Not completed today'}"
        for h in habits
    ])

    prompt = f"""
    You are a friendly wellness coach. User: {current_user.username}.
    Current Habits Status:
    {habit_list_str}
    
    Based on this, please:
    1. Praise a success.
    2. Gently point out one growth area.
    3. Suggest one tiny actionable step.
    Keep the response concise (under 120 words) and in a single paragraph.
    """

    try:
        # Corrected model string and call for new SDK
        response = ai_state.client.models.generate_content(
            model="gemini-2.5-flash",  # Use the correct model name from your GCP console
            contents=prompt,
        )
        return ChatbotResponse(reply=response.text)
    except Exception as e:
        print(f"Gemini API Error: {e}")
        raise HTTPException(status_code=500, detail="The AI coach is currently unavailable.")


