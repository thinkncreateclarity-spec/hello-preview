from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
import os
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

app = FastAPI(title="Ajay's FastAPI - PHASE 4 COMPLETE")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

engine = create_engine(DATABASE_URL or "sqlite:///./test.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class TodoDB(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    complete = Column(Boolean, default=False)
    user_id = Column(Integer)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TodoBase(BaseModel):
    title: str
    complete: bool = False

class TodoCreate(TodoBase):
    pass

class Todo(TodoBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(UserDB).filter(UserDB.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

@app.get("/health")
async def health():
    return {"status": "healthy", "phase": "4-JWT-COMPLETE"}

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <h1>Ajay's FastAPI 🚀 - PHASE 4 LIVE!</h1>
    <p><a href="/docs">Swagger UI → Register/Login/Todos</a></p>
    """

@app.post("/auth/register", response_model=dict)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = UserDB(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()

    db.refresh(db_user)
    return {"msg": "User registered"}

@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/todos/", response_model=Todo)
async def create_todo(todo: TodoCreate, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    db_todo = TodoDB(**todo.dict(), user_id=current_user.id)
    db.add(db_todo)
    db.commit() 

    return db_todo

@app.get("/todos/", response_model=List[Todo])
async def read_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    todos = db.query(TodoDB).filter(TodoDB.user_id == current_user.id).offset(skip).limit(limit).all()
    return todos

@app.get("/todos/{todo_id}", response_model=Todo)
async def read_todo(todo_id: int, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id, TodoDB.user_id == current_user.id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    db_todo = db.query(TodoDB).filter(TodoDB.id == todo_id, TodoDB.user_id == current_user.id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, value in todo.dict().items():
        setattr(db_todo, key, value)
    db.commit()

    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    db_todo = db.query(TodoDB).filter(TodoDB.id == todo_id, TodoDB.user_id == current_user.id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()

    return {"message": f"Todo {todo_id} deleted"}
