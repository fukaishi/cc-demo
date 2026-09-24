import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.environ.get("SHIRITORI_DB", Path(__file__).parent.parent / "shiritori.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS plays (
  id           TEXT PRIMARY KEY,
  player_id    TEXT NOT NULL,
  data_version INTEGER NOT NULL,
  status       TEXT NOT NULL,
  created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS answers (
  play_id    TEXT NOT NULL REFERENCES plays(id),
  step       INTEGER NOT NULL,
  from_word  TEXT NOT NULL,
  choice     TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (play_id, step)
);

CREATE INDEX IF NOT EXISTS idx_answers_node ON answers(from_word, choice);
"""


def connect(path: Path | str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn
