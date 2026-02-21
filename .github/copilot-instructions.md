<!-- Short, focused instructions for AI coding assistants working on this repo -->
# Copilot / AI Agent Instructions

## Big Picture Architecture

**Habit Tracker** is a full-stack app: React SPA (`habit-tracker-frontend/`) + FastAPI backend (`sql_app/`). Data flows: Frontend → Axios client (auth token in headers) → FastAPI (validates JWT, checks ownership) → SQLAlchemy ORM → SQLite.

Key integration: Frontend stores JWT in `localStorage['token']`, axios interceptors attach it to every request as `Authorization: Bearer <token>`. Backend dependency `get_current_user()` validates the token and injects the authenticated user into endpoint handlers.

**New (v0.2+)**: Gemini AI chatbot integration via `google.genai` SDK. Environment variable `GEMINI_API_KEY` enables the `/chatbot/analyze` endpoint, which fetches user habits and sends them to Gemini for motivational feedback.

## Critical Workflows

**Local development**:
- Backend: `uvicorn sql_app.main:app --reload --host 127.0.0.1 --port 8000` (watches `sql_app/` for changes)
- Frontend (in `habit-tracker-frontend/`): `npm start` (runs on `http://localhost:3000`, proxies API to `http://127.0.0.1:8000`)
- Database: Migrations manual—edit `sql_app/models.py`, then uncomment `models.Base.metadata.create_all(bind=engine)` in `main.py` and run backend once to sync, then re-comment it.

**Docker (backend only)**:
```bash
docker build -t habit-backend .
docker run -p 8000:8000 habit-backend
```

## Key Files & Patterns

| File | Purpose |
|------|---------|
| `sql_app/main.py` | FastAPI app, CORS setup, all endpoints, `get_current_user()`, `get_db()`, Gemini integration |
| `sql_app/crud.py` | Database helpers (create/read/delete/update). Always use these; they handle `add()`, `commit()`, `refresh()` |
| `sql_app/models.py` | SQLAlchemy ORM models (User, Habit). `Habit.last_completed_at: Optional[Date]` tracks daily completion status |
| `sql_app/schemas.py` | Pydantic schemas for validation & response serialization. Habit has `HabitCreate`, `HabitUpdate` variants; all have `from_attributes=True` |
| `sql_app/security.py` | JWT creation, password hashing (bcrypt), secrets (`SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES=30`) |
| `habit-tracker-frontend/src/services/api.js` | Axios instance with interceptors for token attachment and 401 handling |

## Patterns & Conventions

**Database operations**: Always delegate to `sql_app/crud.py`. Example pattern (from `crud.create_user`):
```python
db_obj = models.User(...)
db.add(db_obj)
db.commit()
db.refresh(db_obj)
return db_obj
```

**Endpoint ownership checks**: Verify `current_user.id == resource.owner_id` before modifying (see `PUT /habits/{id}`). Raise `HTTPException(403, "Not authorized")` if denied.

**Schemas**: Always use `response_model=schemas.SomeSchema` in endpoint decorator. Pydantic auto-serializes SQLAlchemy models via `from_attributes=True`.

**Auth flow**: 
1. `POST /token` with form data (`username`, `password`) → returns JWT
2. Frontend stores in `localStorage['token']`
3. Axios intercepts and adds `Authorization: Bearer <token>` header
4. Backend `get_current_user(token: str = Depends(oauth2_scheme), db: Session)` validates JWT, fetches user from DB, returns to endpoint

**Habit completion**: Toggle endpoint (`PUT /habits/{id}/toggle`) sets `habit.last_completed_at = date.today()` if not already set today, else clears it (tracks daily completion, not count).

## Adding New Features

**New endpoint?** 
- Add route in `sql_app/main.py` with `current_user = Depends(get_current_user)` if auth required
- Perform ownership check: `if resource.owner_id != current_user.id: raise HTTPException(403, ...)`
- Use crud helpers for DB ops

**New model?**
- Add to `sql_app/models.py` with `__tablename__` and columns
- Create request/response schemas in `sql_app/schemas.py` with `from_attributes=True`
- Add CRUD functions to `sql_app/crud.py`
- Uncomment `models.Base.metadata.create_all()` in `main.py`, run backend once, re-comment

**Gemini integration notes**: 
- Check `genai_client` is not None before calling (may be disabled if `GEMINI_API_KEY` unset)
- Fetch habits from DB, format as text prompt, call `genai_client.models.generate_content(model="gemini-1.5-flash", contents=prompt)`
- Always wrap in try/except and return 500 error on failure (see `/chatbot/analyze`)

## Frontend Notes

- API base URL in `api.js` is hardcoded to `http://127.0.0.1:8000`; update if deploying backend elsewhere
- 401 responses trigger logout and page reload (Axios interceptor)
- Token refresh not implemented—JWT expires after 30 min, user must re-login

## Deployment & Security

- **`SECRET_KEY`** (in `security.py`): Hardcoded for dev; must load from env var / secret manager in production
- **CORS** (in `main.py`): Currently allows `localhost:3000`, GCP IP, and Google Storage. Restrict in production
- **Database**: SQLite file (`sql_app.db`) is committed to `.ebignore` but should be in `.gitignore` for real deployments
- **Environment**: `.env` file loads `GEMINI_API_KEY` via `dotenv.load_dotenv()` at startup
