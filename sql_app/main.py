import os
import logging
from datetime import timedelta, date, datetime
from typing import List, Optional
from contextlib import asynccontextmanager

# AI and LangChain Imports
from google import genai
from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings

# FastAPI and Auth Imports
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- CUSTOM EMBEDDING WRAPPER ---
class GeminiRAGEmbeddings(Embeddings):
    def __init__(self, client):
        self.client = client
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
    models.Base.metadata.create_all(bind=engine)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            # FIX: Removed http_options={'api_version': 'v1'} 
            # This allows the client to find gemini-embedding-001 on the beta endpoint
            ai_state.client = genai.Client(api_key=api_key)
            logger.info("Gemini AI Client initialized (Auto-versioning).")

            if os.path.exists("chroma_db"):
                custom_emb = GeminiRAGEmbeddings(ai_state.client)
                ai_state.vector_db = Chroma(
                    persist_directory="chroma_db", 
                    embedding_function=custom_emb
                )
                logger.info("Knowledge Base (chroma_db) loaded successfully.")
            else:
                logger.warning("'chroma_db' folder not found.")
        except Exception as e:
            logger.error(f"AI Initialization Error: {e}")
    yield
    ai_state.client = None
    ai_state.vector_db = None

app = FastAPI(lifespan=lifespan)

# 3. CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Auth Dependencies
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

@app.post("/chatbot/analyze", response_model=ChatbotResponse)
async def analyze_habits(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not ai_state.client:
        raise HTTPException(status_code=503, detail="AI service is not configured.")

    habits = db.query(models.Habit).filter(models.Habit.owner_id == current_user.id).all()
    if not habits:
        return ChatbotResponse(reply="Add some habits first so I can analyze your progress!")

    today = date.today()
    summary_items = []
    for h in habits:
        status = "COMPLETED" if h.last_completed_at == today else "PENDING"
        summary_items.append(f"Habit: {h.name} | Description: {h.description or 'N/A'} | Status today: {status}")
    
    full_habit_context = "\n".join(summary_items)

    prompt = f"""
    You are a professional wellness coach for {current_user.username}. 
    Current user status:
    {full_habit_context}
    
    Task:
    1. Look at the ENTIRE list.
    2. Provide a holistic review identifying patterns.
    3. Praise discipline or suggest momentum-building steps.
    4. Suggest ONE Micro-Habit to complement this specific set.
    
    Keep response under 150 words, single cohesive paragraph.
    """

    try:
        response = ai_state.client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
        )
        return ChatbotResponse(reply=response.text)
    except Exception as e:
        logger.error(f"Gemini Coach Error: {e}")
        raise HTTPException(status_code=500, detail="AI Coach unavailable.")

@app.post("/chatbot/ask", response_model=ChatbotResponse)
async def ask_chatbot(
    request: ChatRequest, 
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not ai_state.client:
        raise HTTPException(status_code=503, detail="AI Service initializing...")

    try:
        logger.info(f"Processing query for user: {current_user.username}")

        # 1. Fetch Chat Memory
        history = db.query(models.ChatMessage).filter(
            models.ChatMessage.user_id == current_user.id
        ).order_by(models.ChatMessage.timestamp.desc()).limit(6).all()
        history_str = "\n".join([f"{m.role}: {m.content}" for m in reversed(history)])

        # 2. RAG Search
        expert_context = "No expert data found."
        if ai_state.vector_db:
            docs = ai_state.vector_db.similarity_search(request.message, k=2)
            expert_context = "\n".join([d.page_content for d in docs])

        # 3. Personal Context
        user_habits = db.query(models.Habit).filter(models.Habit.owner_id == current_user.id).all()
        habit_ctx = "\n".join([f"- {h.name}: {h.description}" for h in user_habits])

        prompt = f"""
        Role: Wellness Assistant for {current_user.username}.
        History: {history_str}
        Tracked Habits: {habit_ctx}
        Knowledge: {expert_context}
        User Query: {request.message}
        Instruction: Respond concise and helpfully using the context provided.
        """

        response = ai_state.client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        ai_reply = response.text

        # 4. Save to Memory
        db.add(models.ChatMessage(user_id=current_user.id, role="user", content=request.message))
        db.add(models.ChatMessage(user_id=current_user.id, role="model", content=ai_reply))
        db.commit()

        return ChatbotResponse(reply=ai_reply)

    except Exception as e:
        logger.exception("Chatbot pipeline failed")
        raise HTTPException(status_code=500, detail="Internal error occurred.")