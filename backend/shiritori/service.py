import json
import sqlite3
import uuid
from pathlib import Path

from .kana import last_kana
from .routes import Routes

SEED_PATH = Path(__file__).parent / "seed.json"


class PlayNotFound(Exception):
    pass


class InvalidAnswer(Exception):
    pass


class ShiritoriService:
    def __init__(self, conn: sqlite3.Connection, routes: Routes):
        self.conn = conn
        self.routes = routes

    # --- プレイの進行 ---

    def create_play(self, player_id: str) -> dict:
        play_id = str(uuid.uuid4())
        with self.conn:
            self.conn.execute(
                "INSERT INTO plays (id, player_id, data_version, status) VALUES (?, ?, ?, 'playing')",
                (play_id, player_id, self.routes.version),
            )
        return self.state(play_id)

    def answer(self, play_id: str, step: int, choice: str) -> dict:
        play = self._play(play_id)
        history = self._history(play_id)
        if play["status"] != "playing":
            raise InvalidAnswer("このプレイは終了しています")
        if step != len(history) + 1:
            raise InvalidAnswer(f"{len(history) + 1}問目の回答を送ってください")
        from_word = history[-1] if history else self.routes.start
        if choice not in self.routes.choices_for(from_word):
            raise InvalidAnswer(f"{choice} は「{from_word}」の選択肢にありません")

        with self.conn:
            self.conn.execute(
                "INSERT INTO answers (play_id, step, from_word, choice) VALUES (?, ?, ?, ?)",
                (play_id, step, from_word, choice),
            )
            if step == self.routes.max_steps:
                self.conn.execute("UPDATE plays SET status = 'finished' WHERE id = ?", (play_id,))
        return self.state(play_id)

    def state(self, play_id: str) -> dict:
        self._play(play_id)
        history = self._history(play_id)
        word = history[-1] if history else self.routes.start
        finished = len(history) == self.routes.max_steps
        return {
            "play_id": play_id,
            "step": len(history) + 1,
            "max_steps": self.routes.max_steps,
            "history": [self.routes.start, *history],
            "word": word,
            "kana": last_kana(word),
            "choices": [] if finished else self.routes.choices_for(word),
            "finished": finished,
        }

    # --- 集計 ---

    def node_counts(self, from_word: str) -> dict[str, int]:
        """その単語での各選択肢の票数。同じプレイヤーは最初の1回だけ数える。"""
        rows = self.conn.execute(
            """
            SELECT a.choice, COUNT(*) AS n
            FROM answers a JOIN plays p ON p.id = a.play_id
            WHERE a.from_word = :word AND p.data_version = :version
              AND a.rowid = (
                SELECT a2.rowid
                FROM answers a2 JOIN plays p2 ON p2.id = a2.play_id
                WHERE a2.from_word = :word AND p2.data_version = :version
                  AND p2.player_id = p.player_id
                ORDER BY a2.rowid LIMIT 1
              )
            GROUP BY a.choice
            """,
            {"word": from_word, "version": self.routes.version},
        ).fetchall()
        counts = {c: 0 for c in self.routes.choices_for(from_word)}
        counts.update({r["choice"]: r["n"] for r in rows})
        return counts

    def result(self, play_id: str) -> dict:
        self._play(play_id)
        rows = self.conn.execute(
            "SELECT step, from_word, choice FROM answers WHERE play_id = ? ORDER BY step", (play_id,)
        ).fetchall()
        steps = []
        for r in rows:
            counts = self.node_counts(r["from_word"])
            total = sum(counts.values())
            top = max(counts.values())
            steps.append({
                "step": r["step"],
                "from_word": r["from_word"],
                "choice": r["choice"],
                "total": total,
                "counts": counts,
                "rate": round(counts[r["choice"]] / total * 100) if total else 0,
                "is_top": total > 0 and counts[r["choice"]] == top,
            })
        score = round(sum(s["rate"] for s in steps) / len(steps)) if steps else 0
        return {
            "play_id": play_id,
            "finished": len(steps) == self.routes.max_steps,
            "score": score,
            "hits": sum(s["is_top"] for s in steps),
            "steps": steps,
        }

    # --- 初期データ ---

    def seed_if_empty(self, path: Path = SEED_PATH) -> None:
        if self.conn.execute("SELECT 1 FROM plays LIMIT 1").fetchone():
            return
        seed = json.loads(path.read_text(encoding="utf-8"))
        play_id = self.create_play(seed["player_id"])["play_id"]
        for step, choice in enumerate(seed["choices"], start=1):
            self.answer(play_id, step, choice)

    # --- 内部 ---

    def _play(self, play_id: str) -> sqlite3.Row:
        play = self.conn.execute("SELECT * FROM plays WHERE id = ?", (play_id,)).fetchone()
        if play is None:
            raise PlayNotFound(play_id)
        return play

    def _history(self, play_id: str) -> list[str]:
        rows = self.conn.execute(
            "SELECT choice FROM answers WHERE play_id = ? ORDER BY step", (play_id,)
        ).fetchall()
        return [r["choice"] for r in rows]
