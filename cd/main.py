from fastapi import FastAPI, status, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

app = FastAPI(title="Todo App")

class TaskCreate(BaseModel):
    title: str
    description: str

class Task(TaskCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    is_completed: bool

class TaskUpdate(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None

class Database:
    def __init__(self):
        self._tasks: List[Task] = []
        self._next_id = 1

    def add(self, task_create: TaskCreate) -> Task:
        task = Task(
            id=self._next_id,
            title=task_create.title,
            description=task_create.description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_completed=False
        )
        self._tasks.append(task)
        self._next_id += 1
        return task

    def get_all(self) -> List[Task]:
        return self._tasks

    def get_by_id(self, task_id: int) -> Task:
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise HTTPException(status_code=404, detail="Task not found")

    def update(self, task_update: TaskUpdate) -> Task:
        task = self.get_by_id(task_update.id)
        if task_update.title:
            task.title = task_update.title
        if task_update.description:
            task.description = task_update.description
        task.updated_at = datetime.utcnow()
        return task

    def delete(self, task_id: int):
        task = self.get_by_id(task_id)
        self._tasks.remove(task)

    def mark_complete(self, task_id: int) -> Task:
        task = self.get_by_id(task_id)
        task.is_completed = True
        task.updated_at = datetime.utcnow()
        return task

    def search(self, query: str) -> List[Task]:
        query = query.lower()
        return [
            task for task in self._tasks
            if query in task.title.lower() or query in task.description.lower()
        ]

db = Database()

@app.get("/")
def index():
    return {"message": "Todo App"}

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    new_task = db.add(task)
    return {
        "success": True,
        "data": new_task,
        "message": "Task created successfully"
    }

@app.get("/tasks")
def get_tasks():
    return {"data": db.get_all()}

@app.patch("/tasks")
def update_task(task: TaskUpdate):
    if not task.title and not task.description:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field is required to update"
        )
    updated = db.update(task)
    return {
        "success": True,
        "data": updated,
        "message": "Task updated successfully"
    }

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    db.delete(task_id)
    return {
        "success": True,
        "message": f"Task {task_id} deleted successfully"
    }

@app.patch("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    task = db.mark_complete(task_id)
    return {
        "success": True,
        "data": task,
        "message": f"Task {task_id} marked as complete"
    }


