from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title:str
app = FastAPI()

tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Walk the Dog", "done": False},
    {"id": 3, "title": "Write code", "done": True},

]

@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks(): #list tasks
    return tasks

@app.get("/tasks/{id}")
def get_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})

@app.post("/tasks")
def create_task(new_task: TaskCreate): #creates a new task
    if new_task.title == "":
        return JSONResponse(status_code=400, content={"error": "title is required"})
    next_id = len(tasks)+1
    task = {"id": next_id, "title": new_task.title, "done": False}
    tasks.append(task)
    return JSONResponse(status_code=201, content=task)