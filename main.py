from contextlib import asynccontextmanager
import sqlite3
from fastapi import FastAPI, HTTPException, status, Response, Query
from init_db import DB_NAME, init_db
from pydantic import BaseModel
from typing import Optional

def get_db_connection():
  conn = sqlite3.connect(DB_NAME)
  conn.row_factory = (
      sqlite3.Row
  )  # Enables accessing columns by name and dict conversion
  return conn

@asynccontextmanager
async def lifespan(app: FastAPI):
  init_db()  # Runs on server startup
  yield


app = FastAPI(lifespan=lifespan)


class TaskCreate(BaseModel):
    title: str
    done: bool = False

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

@app.get("/health", summary="Health check")
def health():
    """Check if the server is healthy and running."""
    return {"status": "ok"}


@app.get("/", summary="Root endpoint")
def root():
  return {"name": "Task API", "version": "2.0", "endpoints": ["/tasks"]}


@app.get("/tasks", summary="List tasks with search, filter, and sorting")
def get_tasks(
    search: Optional[str] = Query(None, description="Search term for title"),
    done: Optional[bool] = Query(None, description="Filter by done status"),
    sort: Optional[str] = Query("id", description="Sort by 'title', 'id', or 'done'"),
):
  query = "SELECT id, title, done FROM tasks WHERE 1=1"
  params = []

  # 1. Search with SQL LIKE
  if search:
    query += " AND title LIKE ?"
    params.append(f"%{search}%")

  # 2. Filter with SQL WHERE
  if done is not None:
    query += " AND done = ?"
    params.append(int(done))

  # 3. Sort with SQL ORDER BY (whitelisting columns for safety)
  allowed_sort_fields = {"id": "id", "title": "title", "done": "done"}
  sort_field = allowed_sort_fields.get(sort, "id")
  query += f" ORDER BY {sort_field} ASC"

  with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    return [
        {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
        for row in rows
    ]

@app.get("/tasks/{id}", summary="Get tasks by ID")
def get_task(id: int):
  with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (id,)
    ) 
    row = cursor.fetchone()

    if not row:
      raise HTTPException(
          status_code=404, detail={"error": "Task not found"}
      )

    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create a new task")
def create_task(payload: TaskCreate):
    # Validation: title cannot be empty or just whitespace
    if not payload.title or not payload.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Title is required and cannot be empty"},
        )

    clean_title = payload.title.strip()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Insert into database
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (clean_title, int(payload.done))
        )
        conn.commit()

        new_id = cursor.lastrowid

    return {
        "id": new_id,
        "title": clean_title,
        "done": payload.done
    }
    
@app.put("/tasks/{id}", summary="Update task title and/or done property using its ID")
def update_task(id: int, task_data: TaskUpdate):
  # 1. Validate: Reject empty payload
  if task_data.title is None and task_data.done is None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Request body cannot be empty.",
    )

  # 2. Validate: Title cannot be an empty string if provided
  if task_data.title is not None and not task_data.title.strip():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Title cannot be empty."
    )

  with get_db_connection() as conn:
    cursor = conn.cursor()

    # Check if task exists
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (id,))
    current_task = cursor.fetchone()

    if not current_task:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND, detail="Unknown Id."
      )

    # Determine updated values (retain current value if None)
    new_title = (
        task_data.title.strip()
        if task_data.title is not None
        else current_task["title"]
    )
    new_done = (
        int(task_data.done)
        if task_data.done is not None
        else current_task["done"]
    )

    # Run SQL UPDATE
    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, id),
    )
    conn.commit()

    return {"id": id, "title": new_title, "done": bool(new_done)}

@app.delete("/tasks/{id}",status_code=status.HTTP_204_NO_CONTENT,summary="Delete a task using its ID")
def delete_task(id: int):
  with get_db_connection() as conn:
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (id,))
    if not cursor.fetchone():
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND, detail="Unknown Id."
      )

    cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

