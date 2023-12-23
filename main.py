from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Used sqlite here for testing the api
DATABASE_URL = "sqlite:///./task.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()


# This is the Task Model as described in the problem description
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True) # to have unique title
    description = Column(String)
    completed = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/tasks/", response_model=None, summary="Create a new task")
def create_task(task: dict, db: Session = Depends(get_db)):
    db_task = Task(**task)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/tasks/{task_id}", response_model=None, summary="Get a task by ID")
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@app.put("/tasks/{task_id}", response_model=None, summary="Update a task by ID")
def update_task(task_id: int, updated_task: dict, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in updated_task.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/tasks/{task_id}", response_model=dict, summary="Delete a task by ID")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(db_task)
    db.commit()

    return {"message": "Task deleted successfully"}


@app.get("/tasks/", response_model=None, summary="Get all tasks with optional completion filters")
def read_tasks(completed: bool = None, db: Session = Depends(get_db)):
    query = db.query(Task)

    if completed is not None:
        query = query.filter(Task.completed == completed)

    tasks = query.all()
    return tasks
# http://localhost:8000/tasks/?completed=false
