from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Todo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
todos: list[dict] = []
next_id = 1


class TodoCreate(BaseModel):
    title: str


class TodoResponse(BaseModel):
    id: int
    title: str
    completed: bool


@app.get("/todos", response_model=list[TodoResponse])
def list_todos(status: str | None = Query(None, pattern="^(completed|active)$")):
    if status == "completed":
        return [t for t in todos if t["completed"]]
    if status == "active":
        return [t for t in todos if not t["completed"]]
    return todos


@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(body: TodoCreate):
    global next_id
    todo = {"id": next_id, "title": body.title, "completed": False}
    next_id += 1
    todos.append(todo)
    return todo


@app.patch("/todos/{todo_id}", response_model=TodoResponse)
def toggle_todo(todo_id: int):
    for todo in todos:
        if todo["id"] == todo_id:
            todo["completed"] = not todo["completed"]
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            todos.pop(i)
            return
    raise HTTPException(status_code=404, detail="Todo not found")
