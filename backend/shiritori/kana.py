SMALL_TO_LARGE = {
    "ぁ": "あ", "ぃ": "い", "ぅ": "う", "ぇ": "え", "ぉ": "お",
    "ゃ": "や", "ゅ": "ゆ", "ょ": "よ", "っ": "つ", "ゎ": "わ",
}

VOWEL_ROWS = [
    ("あかさたなはまやらわがざだばぱ", "あ"),
    ("いきしちにひみりぎじぢびぴ", "い"),
    ("うくすつぬふむゆるぐずづぶぷ", "う"),
    ("えけせてねへめれげぜでべぺ", "え"),
    ("おこそとのほもよろをごぞどぼぽ", "お"),
]


def to_hiragana(text: str) -> str:
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in text)


def _vowel_of(kana: str) -> str:
    for chars, vowel in VOWEL_ROWS:
        if kana in chars:
            return vowel
    return kana


def last_kana(word: str) -> str:
    """しりとりで次に繋ぐ文字。長音は直前の母音、小書き文字は大きい文字として扱う。"""
    chars = to_hiragana(word)
    last = chars[-1]
    if last == "ー":
        prev = chars[-2]
        last = _vowel_of(SMALL_TO_LARGE.get(prev, prev))
    return SMALL_TO_LARGE.get(last, last)


def first_kana(word: str) -> str:
    return to_hiragana(word)[0]
