from contextlib import asynccontextmanager
from fastapi import FastAPI
from init_db import init_db  


@asynccontextmanager
async def lifespan(app: FastAPI):
  init_db()  # Runs on server startup
  yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
  return {"name": "Task API (SQLite)", "version": "2.0"}


# Your Stage 1, 2, 3... endpoints will go below here

# INITIAL_TASKS = [
#     {"id":1, "title":"study", "done":False},
#     {"id":2, "title":"sleep", "done":True},
#     {"id":3, "title":"exercise", "done":False}
# ]

# task_list = [
#     {"id":1, "title":"study", "done":False},
#     {"id":2, "title":"sleep", "done":True},
#     {"id":3, "title":"exercise", "done":False}
# ]

# task_id_counter = 4

# class TaskCreate(BaseModel):
#     title: str

# class TaskUpdate(BaseModel):
#     title: Optional[str] = None
#     done: Optional[bool] = None

# @app.get("/", summary="Root Endpoint")
# def root():
#     """Return API name, version, and available endpoints."""
#     return {
#         "name" : "Task API",
#         "version" : "1.0",
#         "endpoints" : ["/tasks"]
#     }

# @app.get("/health", summary="Health check")
# def health():
#     """Check if the server is healthy and running."""
#     return {"status": "ok"}


# @app.get("/tasks", summary="Filter by query parameter if done is provided else List all tasks. Added search functionality as well.")
# def get_task(done : Optional[bool] = None, search: Optional[str] = None):
#     """Filter tasks based on the value of done. If no query parameter 
#     passed then retrieve the full list of all tasks. Also you can search a task using a keyword and retrieve it."""
#     results = task_list
#     if done is not None:
#         results = [t for t in results if t["done"] == done]
#     if search is not None and search.strip():
#         term = search.strip().lower()
#         results = [t for t in results if term in t["title"].lower()]

#     return results

# @app.get("/tasks/{id}", summary="Get task by ID")
# def get_task_by_id(id:int):
#     """Retrieve a single task by its unique numeric ID."""
#     task = next((t for t in task_list if t["id"] == id), None)
#     if(task is not None):
#         return task
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, 
#             detail=f"error: Task {id} not found"
#             )

# @app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create a new task")
# def create_task(payload: TaskCreate):
#     """Create a new task with a title and default 'done' status as false."""
#     global task_id_counter

#     if not payload.title or not payload.title.strip():
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Title is required and cannot be empty",
#         )

#     new_task = {
#         "id": task_id_counter,
#         "title": payload.title.strip(),
#         "done": False,
#     }

#     task_list.append(new_task)
#     task_id_counter += 1

#     return new_task
    
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