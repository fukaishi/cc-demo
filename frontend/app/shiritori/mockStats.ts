// サンプル用のダミー集計。保存はせず、単語から決まる疑似的な票数を返す。
function hash(text: string): number {
  let h = 2166136261;
  for (const c of text) {
    h ^= c.codePointAt(0)!;
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

export type NodeStats = {
  total: number;
  counts: Record<string, number>;
};

export function mockStats(fromWord: string, choices: string[]): NodeStats {
  const counts: Record<string, number> = {};
  choices.forEach((choice, i) => {
    // 先頭の選択肢ほど票が入りやすいように重みをつける
    counts[choice] = 5 + (hash(fromWord + choice) % 60) + (choices.length - i) * 10;
  });
  const total = Object.values(counts).reduce((a, b) => a + b, 0);
  return { total, counts };
}
