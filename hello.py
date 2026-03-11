from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List
import os

app = FastAPI(title="Ajay's FastAPI - Phase 2 Postgres")

@app.get("/health")
async def health():
    return {"status": "healthy", "pr": "#1", "todos": "ready"}

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <h1>Ajay's FastAPI 🚀 - PHASE 2 POSTGRES LIVE!</h1>
    <p>✅ FastAPI + Railway Postgres + CRUD endpoints</p>
    <p><a href="/docs">Swagger UI → Test CRUD</a></p>
    <p><a href="/todos/">GET all todos</a></p>
    """

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

engine = create_engine(DATABASE_URL or "sqlite:///./test.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TodoDB(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    complete = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# Pydantic models
class TodoBase(BaseModel):
    title: str
    complete: bool = False

class TodoCreate(TodoBase):
    pass

class Todo(TodoBase):
    id: int
    class Config:
        from_attributes = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD Endpoints
@app.post("/todos/", response_model=Todo)
async def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = TodoDB(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos/", response_model=List[Todo])
async def read_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    todos = db.query(TodoDB).offset(skip).limit(limit).all()
    return todos

@app.get("/todos/{todo_id}", response_model=Todo)
async def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    for key, value in todo.dict().items():
        setattr(db_todo, key, value)
    
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(db_todo)
    db.commit()
    return {"message": f"Todo {todo_id} deleted"}
