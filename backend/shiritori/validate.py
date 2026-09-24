"""ルートデータの検証。`python -m shiritori.validate` で実行する。"""

import sys

from .kana import first_kana, last_kana
from .routes import Routes, load_routes

CHOICE_COUNT = 4


def validate(routes: Routes) -> list[str]:
    errors: list[str] = []

    for kana, words in routes.choices_by_kana.items():
        if len(words) != CHOICE_COUNT:
            errors.append(f"「{kana}」の選択肢が{len(words)}個")
        for word in words:
            if first_kana(word) != kana:
                errors.append(f"{word} は「{kana}」で始まらない")
            if last_kana(word) == "ん":
                errors.append(f"{word} は「ん」で終わる")

    reached: set[str] = set()
    paths = 0

    def walk(path: list[str]) -> None:
        nonlocal paths
        if len(path) - 1 == routes.max_steps:
            paths += 1
            return
        kana = last_kana(path[-1])
        reached.add(kana)
        choices = routes.choices_by_kana.get(kana)
        if not choices:
            errors.append(f"{' → '.join(path)} の次（「{kana}」）の選択肢がない")
            return
        for choice in choices:
            if choice in path:
                errors.append(f"同じ単語が再登場: {' → '.join(path + [choice])}")
                continue
            walk(path + [choice])

    walk([routes.start])

    for kana in routes.choices_by_kana:
        if kana not in reached:
            errors.append(f"「{kana}」の選択肢に到達するルートがない")

    return errors


def main() -> int:
    routes = load_routes()
    errors = validate(routes)
    words = sum(len(w) for w in routes.choices_by_kana.values())
    print(f"文字: {len(routes.choices_by_kana)} / 単語: {words}")
    for e in errors:
        print(e)
    print("OK" if not errors else f"NG: {len(errors)}件")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
