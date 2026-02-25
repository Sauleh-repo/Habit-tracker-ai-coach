import os
from datetime import timedelta, date
from typing import List, Optional
from contextlib import asynccontextmanager

# SDK and FastAPI imports
from google import genai
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Phase 2: LangChain & Vector Store
from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings

from . import crud, models, schemas, security
from .database import SessionLocal, engine

# 1. Configuration & Global State
load_dotenv()

# --- CUSTOM EMBEDDING WRAPPER ---
# This ensures the backend uses the exact same model and logic that ingest.py used
class GeminiRAGEmbeddings(Embeddings):
    def __init__(self, client):
        self.client = client
        # Exact string verified by your diagnostic script
        self.model_name = "models/gemini-embedding-001"

    def embed_documents(self, texts: List[str]):
        res = self.client.models.embed_content(
            model=self.model_name, 
            contents=texts, 
            config={'task_type': 'retrieval_document'}
        )
        return [item.values for item in res.embeddings]

    def embed_query(self, text: str):
        res = self.client.models.embed_content(
            model=self.model_name, 
            contents=text, 
            config={'task_type': 'retrieval_query'}
        )
        return res.embeddings[0].values

class AIState:
    client: Optional[genai.Client] = None
    vector_db: Optional[Chroma] = None

ai_state = AIState()

# 2. Lifespan: Auto-starts the Database, AI Client, and Knowledge Base
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables if they don't exist
    models.Base.metadata.create_all(bind=engine)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            # Initialize Gemini Client (for Chat and Analysis)
            ai_state.client = genai.Client(api_key=api_key)
            print("Gemini AI Client (2.5 Flash) initialized.")

            # Load Vector Database (for Knowledge Chatbot)
            if os.path.exists("chroma_db"):
                custom_emb = GeminiRAGEmbeddings(ai_state.client)
                ai_state.vector_db = Chroma(
                    persist_directory="chroma_db", 
                    embedding_function=custom_emb
                )
                print("Knowledge Base (chroma_db) loaded successfully.")
            else:
                print("Warning: 'chroma_db' folder not found. Conversational chat will be disabled.")
        except Exception as e:
            print(f"AI Initialization Error: {e}")
    else:
        print("Warning: GOOGLE_API_KEY not found in .env file.")
    
    yield
    # Cleanup on shutdown
    ai_state.client = None
    ai_state.vector_db = None

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

# 7. AI Chatbot Endpoints
class ChatbotResponse(BaseModel):
    reply: str

class ChatRequest(BaseModel):
    message: str

# PHASE 1: Proactive Habit Coach (Uses Habit Data)
@app.post("/chatbot/analyze", response_model=ChatbotResponse)
async def analyze_habits(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not ai_state.client:
        raise HTTPException(status_code=503, detail="AI service is not configured.")

    # Fetch ALL habits for the user
    habits = db.query(models.Habit).filter(models.Habit.owner_id == current_user.id).all()
    
    if not habits:
        return ChatbotResponse(reply="You haven't added any habits yet! Add a few so I can give you a full review.")

    today = date.today()
    
    # 1. Create a more detailed summary for the AI
    summary_items = []
    for h in habits:
        status = "COMPLETED" if h.last_completed_at == today else "PENDING"
        summary_items.append(f"Habit: {h.name} | Description: {h.description or 'N/A'} | Status today: {status}")
    
    full_habit_context = "\n".join(summary_items)

    print(full_habit_context)

    # 2. Updated Prompt to force holistic analysis
    prompt = f"""
    You are a high-level wellness coach for {current_user.username}. 
    Below is a complete list of the user's current habits and their status for today:
    
    {full_habit_context}
    
    Task:
    1. Look at the ENTIRE list above. Do not just focus on the first item.
    2. Provide a holistic review. Mention specific patterns you see across multiple habits.
    3. If they have several completed, praise their overall discipline. 
    4. If they have several pending, give a single piece of advice that helps them get started on multiple fronts.
    5. Suggest ONE "Micro-Habit" that would complement this specific set of habits.
    
    Keep the response under 150 words, encouraging, and formatted as a single cohesive paragraph.
    """

    try:
        response = ai_state.client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
        )
        return ChatbotResponse(reply=response.text)
    except Exception as e:
        print(f"Gemini Coach Error: {e}")
        raise HTTPException(status_code=500, detail="The AI coach is currently unavailable.")
    
# PHASE 2: Conversational Knowledge Assistant (Uses Text Files / RAG)
@app.post("/chatbot/ask", response_model=ChatbotResponse)
async def ask_chatbot(
    request: ChatRequest, 
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db) # Added database dependency
):
    if not ai_state.client or not ai_state.vector_db:
        raise HTTPException(status_code=503, detail="Knowledge base not ready.")

    try:
        # 1. Fetch User's current habits for personal context
        user_habits = db.query(models.Habit).filter(models.Habit.owner_id == current_user.id).all()
        habit_context = "User's current tracked habits:\n"
        if user_habits:
            for h in user_habits:
                habit_context += f"- {h.name}: {h.description or 'No description'}\n"
        else:
            habit_context += "- No habits tracked yet.\n"

        # 2. Similarity Search in knowledge base for expert context
        docs = ai_state.vector_db.similarity_search(request.message, k=3)
        expert_context = "\n".join([doc.page_content for doc in docs])

        # 3. Build the UNIFIED Prompt
        prompt = f"""
        You are a wellness assistant for {current_user.username}.
        
        {habit_context}
        
        Expert Knowledge Context from your files:
        {expert_context}
        
        User Question: {request.message}
        
        Instruction: 
        Use the 'User's current tracked habits' to personalize your answer. 
        If they ask about their own patterns (like sleep), look at their tracked habits first.
        Then, use the 'Expert Knowledge Context' to give them actionable advice.
        Be encouraging and concise.
        """

        # 4. Generate Answer
        response = ai_state.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return ChatbotResponse(reply=response.text)
        
    except Exception as e:
        print(f"RAG Chatbot Error: {e}")
        raise HTTPException(status_code=500, detail="The assistant is having trouble answering.")