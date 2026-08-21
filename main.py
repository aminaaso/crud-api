from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import sqlite3
def lifespan(app):
    """Creates the tasks table if missing, and seeds 3 example tasks only if the table is empty."""
    conn = sqlite3.connect("tasks.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT, done INTEGER)")
    cur.execute("SELECT COUNT(*) FROM tasks")
    count = cur.fetchone()[0]
    if count == 0:
        cur.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Buy milk", 0))
        cur.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Walk the Dog", 0))
        cur.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Write code", 1))
    conn.commit()
    conn.close()
    yield

def get_connection():
    conn = sqlite3.connect("tasks.db")
    return conn

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

class TaskCreate(BaseModel):
    title:str
app = FastAPI(lifespan=lifespan)

tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Walk the Dog", "done": False},
    {"id": 3, "title": "Write code", "done": True},

]

@app.get("/")
def root():
    """Return basic info about this API."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks(): #list tasks
    """Return the full list of tasks."""
    return tasks

@app.get("/tasks/{id}")
def get_task(id: int):
    """Return a single task by its id, or 404 if it doesn't exist."""
    for task in tasks:
        if task["id"] == id:
            return task
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})

@app.post("/tasks")
def create_task(new_task: TaskCreate): #creates a new task
    """Create a new task from the request body."""
    if new_task.title == "":
        return JSONResponse(status_code=400, content={"error": "title is required"})
    next_id = len(tasks)+1
    task = {"id": next_id, "title": new_task.title, "done": False}
    tasks.append(task)
    return JSONResponse(status_code=201, content=task)

@app.put("/tasks/{id}")
def update_task(id: int, updated: TaskUpdate):
    """Update a task's title and/or done status."""
    for task in tasks:
        if task["id"] ==id:
            if updated.title is not None:
               if updated.title == "":
                 return JSONResponse(status_code=400, content = {"error": "Title can not be empty"})
               task["title"] = updated.title
            if updated.done is not None:
               task["done"] = updated.done
            return task
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})

@app.delete("/tasks/{id}")
def delete_task(id: int):
    """Delete a task by id."""
    for task in tasks:
        if task["id"] == id:
            tasks.remove(task)
            return Response(status_code=204)
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
