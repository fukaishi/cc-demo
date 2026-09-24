const SMALL_TO_LARGE: Record<string, string> = {
  ぁ: "あ", ぃ: "い", ぅ: "う", ぇ: "え", ぉ: "お",
  ゃ: "や", ゅ: "ゆ", ょ: "よ", っ: "つ", ゎ: "わ",
};

const VOWEL_ROWS: [string, string][] = [
  ["あかさたなはまやらわがざだばぱ", "あ"],
  ["いきしちにひみりぎじぢびぴ", "い"],
  ["うくすつぬふむゆるぐずづぶぷ", "う"],
  ["えけせてねへめれげぜでべぺ", "え"],
  ["おこそとのほもよろをごぞどぼぽ", "お"],
];

export function toHiragana(text: string): string {
  return text.replace(/[ァ-ヶ]/g, (c) =>
    String.fromCharCode(c.charCodeAt(0) - 0x60),
  );
}

function vowelOf(kana: string): string {
  const row = VOWEL_ROWS.find(([chars]) => chars.includes(kana));
  return row ? row[1] : kana;
}

// しりとりで次に繋ぐ文字。長音は直前の母音、小書き文字は大きい文字として扱う。
export function lastKana(word: string): string {
  const chars = [...toHiragana(word)];
  let last = chars[chars.length - 1];
  if (last === "ー") {
    last = vowelOf(SMALL_TO_LARGE[chars[chars.length - 2]] ?? chars[chars.length - 2]);
  }
  return SMALL_TO_LARGE[last] ?? last;
}

export function firstKana(word: string): string {
  return [...toHiragana(word)][0];
}
