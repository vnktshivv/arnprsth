from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    completed = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

class TodoCreate(BaseModel):
    title: str

class TodoResponse(BaseModel):
    id: int
    title: str
    completed: bool

    class Config:
        orm_mode = True

@app.get("/todos", response_model=List[TodoResponse])
def get_todos():
    db = SessionLocal()
    todos = db.query(Todo).all()
    db.close()
    return todos

@app.post("/todos", response_model=TodoResponse)
def add_todo(todo: TodoCreate):
    db = SessionLocal()
    new_todo = Todo(title=todo.title)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    db.close()
    return new_todo

@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int):
    db = SessionLocal()
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        db.close()
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.completed = not todo.completed
    db.commit()
    db.refresh(todo)
    db.close()
    return todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    db = SessionLocal()
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        db.close()
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    db.close()
    return {"detail": "Todo deleted"}