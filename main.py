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
    conn = get_connection()   
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks")
    rows = cur.fetchall()
    result = []
    for row in rows:      
        task_dict = {"id": row[0], "title": row[1], "done": bool(row[2])}
        result.append(task_dict)
    conn.close()
    return result

@app.get("/tasks/{id}")
def get_task(id: int):
    """Return a single task by its id, or 404 if it doesn't exist."""
    conn = get_connection()   
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = cur.fetchone()
    if row is None:
       return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
    task_dict = {"id": row[0], "title": row[1], "done": bool(row[2])}
    conn.close()
    return task_dict

@app.post("/tasks")
def create_task(new_task: TaskCreate): #creates a new task
    """Create a new task from the request body."""
    if new_task.title == "":
        return JSONResponse(status_code=400, content={"error": "title is required"})
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (new_task.title, 0))
    new_id = cur.lastrowid
    conn.commit()
    task = {"id": new_id, "title": new_task.title, "done": False}
    conn.close()
    return JSONResponse(status_code=201, content=task)
  
@app.put("/tasks/{id}")
def update_task(id: int, updated: TaskUpdate):
    """Update a task's title and/or done status."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = cur.fetchone()
    if row is None:
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
    new_title = row[1]          # start with the current title as default
    if updated.title is not None:
        if updated.title == "":
            return JSONResponse(status_code=400, content = {"error": "Title can not be empty"})
        new_title = updated.title 
    new_done = row[2]
    if updated.done is not None:
        new_done = updated.done
    cur.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (new_title, new_done, id))
    conn.commit()
    task = {"id": id, "title": new_title, "done": bool(new_done)}
    conn.close()
    return task


@app.delete("/tasks/{id}")
def delete_task(id: int):
    """Delete a task by id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = cur.fetchone()
    if row is None:
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
    cur.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return Response(status_code=204)
