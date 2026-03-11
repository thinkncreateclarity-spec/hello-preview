from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List
from passlib.context import CryptContext
import os
import uvicorn
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
from jose import JWTError, jwt

# ========================================
# DATABASE SETUP
# ========================================
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========================================
# MODELS
# ========================================
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    completed = Column(String, default="false")
    owner_id = Column(Integer)

# ========================================
# CREATE TABLES
# ========================================
# ========================================
# PYDANTIC SCHEMAS
# ========================================
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    password_confirm: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str

class TodoCreate(BaseModel):
    title: str
    description: str

class TodoOut(BaseModel):
    id: int
    title: str
    description: str
    completed: str
    owner_id: int

class Token(BaseModel):
    access_token: str
    token_type: str

# ========================================
# SECURITY
# ========================================
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ========================================
# FASTAPI APP
# ========================================
app = FastAPI(title="Ajay's Task Tracker API")
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
# ========================================
# ROUTES - PUBLIC
# ========================================

@app.get("/", response_class=HTMLResponse)
async def root():
    pr = os.environ.get('PR_NUMBER', 'main')
    return f"""
    <h1>Ajay's FastAPI 🚀 - PHASE 2 LIVE!</h1>
    <h2>PostgreSQL + JWT Auth + Todos CRUD</h2>
    <p>PR #{pr} live on Railway!</p>
    <p><a href="/docs">FastAPI Swagger UI → /docs</a></p>
    <p><a href="/todos/">Public Todos → /todos/</a></p>
    """

@app.get("/health")
async def health():
    return {"status": "healthy", "pr": os.environ.get('PR_NUMBER', 'main')}

# ========================================
# AUTH ROUTES
# ========================================
@app.post("/auth/register", response_model=UserOut, status_code=201)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    if user.password != user.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords don't match")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ========================================
# TODOS ROUTES
# ========================================
@app.get("/todos/", response_model=List[TodoOut])
async def read_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    todos = db.query(Todo).offset(skip).limit(limit).all()
    return todos

@app.post("/todos/", response_model=TodoOut, status_code=201)
async def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo(**todo.dict(), owner_id=1)  # Hardcoded for now
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# ========================================
# STARTUP
# ========================================
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
