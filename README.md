# Task API

A simple REST API for managing a to-do list — create, read, update, and delete tasks. Built with FastAPI as part of my Backend AI Internship at FlyRank.

## Run it

```bash
git clone https://github.com/aminaaso/crud-api.git
cd crud-api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | / | API info |
| GET | /health | Health check |
| GET | /tasks | List all tasks |
| POST | /tasks | Create a new task |
| GET | /tasks/{id} | Get a single task |
| PUT | /tasks/{id} | Update a task's title and/or done status |
| DELETE | /tasks/{id} | Delete a task |

## Example request
curl.exe -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title": "Buy eggs"}'

HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy eggs","done":false}


## Swagger UI

![Swagger UI](screenshots/swagger.png)

## Database 

SQLite is serverless and stored in a single file, requiring zero setup and no separate database server. Since it survives restarts, it's ideal for a lightweight project like this.

The database lives in tasks.db, created automatically the first time the app runs. It's git-ignored so that anyone cloning this repo starts with a clean database — they'll see the 3 seeded example tasks instead of my leftover test data.

![Database](screenshots/database.png)

**Query:**
```sql
UPDATE tasks SET done = 1;

```
**What happened:**  Before clicking "Write Changes" in DB Browser, my live API still showed the old values (e.g. task 1 as done:false). After clicking "Write Changes," a fresh GET /tasks immediately showed all 6 tasks marked done:true — with no server restart needed, since the API and DB Browser both read the same tasks.db file

## Notes

Data is now stored persistently in a SQLite database (tasks.db), not in memory. Restarting the server no longer resets your tasks — they remain exactly as you left them.
