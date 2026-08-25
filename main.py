from contextlib import asynccontextmanager
import sqlite3
from fastapi import FastAPI, HTTPException, status
from init_db import DB_NAME, init_db
from pydantic import BaseModel

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
# class TaskUpdate(BaseModel):
#     title: Optional[str] = None
#     done: Optional[bool] = None

@app.get("/health", summary="Health check")
def health():
    """Check if the server is healthy and running."""
    return {"status": "ok"}


@app.get("/")
def root():
  return {"name": "Task API", "version": "2.0", "endpoints": ["/tasks"]}


# 1. GET ALL TASKS
@app.get("/tasks")
def get_tasks():
  with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()

    # Convert SQLite rows into clean Python dictionaries (with boolean 'done')
    tasks = [
        {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
        for row in rows
    ]
    return tasks


# 2. GET SINGLE TASK BY ID
@app.get("/tasks/{id}")
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

        # 2. Retrieve the auto-generated ID from SQLite
        new_id = cursor.lastrowid

    # 3. Return the created task object
    return {
        "id": new_id,
        "title": clean_title,
        "done": payload.done
    }
    
# @app.put("/tasks/{id}", summary="Update task title and/or done using its ID")
# def update_task(id: int, task_data: TaskUpdate):
#     """Updates the title and/or done property of an existing task using its ID if it exists."""
#     task = next((t for t in task_list if t["id"] == id), None)
#     if task is None:
#         raise HTTPException(status_code=404, detail="Unknown Id.")

#     # Reject empty payload
#     if task_data.title is None and task_data.done is None:
#         raise HTTPException(status_code=400, detail="Request body cannot be empty.")

#     if task_data.title is not None:
#         if not task_data.title.strip():
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Title cannot be empty."
#             )
#         task["title"] = task_data.title.strip()

#     if task_data.done is not None:
#         task["done"] = task_data.done

#     return task   

# @app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task using its ID")
# def delete_task(id: int):
#     """Delete a task using its ID if it exists."""
#     task = next((t for t in task_list if t["id"] == id), None)
#     if task is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, 
#             detail="Unknown Id."
#         )

#     task_list.remove(task)
#     return Response(status_code=status.HTTP_204_NO_CONTENT)

# @app.get("/stats", summary="Added stat endpoint")
# def get_stats():
#     """Added stat endpoint where total is the numner of task in task_list, done_count is the count
#     of copmpleted task and open_ount is the count of incomplete task."""
#     total = len(task_list)
#     done_count = sum(1 for t in task_list if t["done"])
#     open_count = total - done_count

#     return {
#         "total": total,
#         "done": done_count,
#         "open": open_count
#     }

# @app.post("/reset", summary="Added reset endpoint to reset the task_list back to what it originally had")
# def reset_tasks():
#     """Added a reset endpoint to roll back task_list"""
#     global task_list, task_id_counter
    
#     task_list = [task.copy() for task in INITIAL_TASKS]
#     task_id_counter = 4

#     return {"message": "Tasks reset to initial state", "tasks": task_list}