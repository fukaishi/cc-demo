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

## しりとりんご

| Method | Path | Description |
|--------|------|-------------|
| POST | /shiritori/plays | Start a play (`{"player_id": "..."}`) |
| GET | /shiritori/plays/{id} | Current state |
| POST | /shiritori/plays/{id}/answers | Answer (`{"step": 1, "choice": "りんご"}`) |
| GET | /shiritori/plays/{id}/result | Result with vote counts |

Answers are stored in SQLite (`shiritori.db`, override with `SHIRITORI_DB`).
Route data is `shiritori/routes.json`.

```bash
python -m shiritori.validate          # validate route data
pip install -r requirements-dev.txt
pytest                                # run tests
```
