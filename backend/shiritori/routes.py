import json
from pathlib import Path

from .kana import last_kana

ROUTES_PATH = Path(__file__).parent / "routes.json"


class Routes:
    def __init__(self, data: dict):
        self.version: int = data["version"]
        self.start: str = data["start"]
        self.max_steps: int = data["maxSteps"]
        self.choices_by_kana: dict[str, list[str]] = data["choicesByKana"]

    def choices_for(self, word: str) -> list[str]:
        return self.choices_by_kana.get(last_kana(word), [])


def load_routes(path: Path = ROUTES_PATH) -> Routes:
    return Routes(json.loads(path.read_text(encoding="utf-8")))
