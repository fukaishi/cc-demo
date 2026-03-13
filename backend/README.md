# Todo API

A simple FastAPI backend for a Todo app with in-memory storage.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /todos | List all todos (optional `?status=completed\|active`) |
| POST | /todos | Create a todo (`{"title": "..."}`) |
| PATCH | /todos/{id} | Toggle completed status |
| DELETE | /todos/{id} | Delete a todo |
