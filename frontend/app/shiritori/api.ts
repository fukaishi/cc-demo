const API_URL = "http://localhost:8000/shiritori";
const PLAYER_KEY = "shiritori-player-id";

export type PlayState = {
  play_id: string;
  step: number;
  max_steps: number;
  history: string[];
  word: string;
  kana: string;
  choices: string[];
  finished: boolean;
};

export type StepResult = {
  step: number;
  from_word: string;
  choice: string;
  total: number;
  counts: Record<string, number>;
  rate: number;
  is_top: boolean;
};

export type PlayResult = {
  play_id: string;
  finished: boolean;
  score: number;
  hits: number;
  steps: StepResult[];
};

// 端末ごとの匿名ID。保存できない環境ではその場限りのIDを使う。
function playerId(): string {
  try {
    const saved = localStorage.getItem(PLAYER_KEY);
    if (saved) return saved;
    const id = crypto.randomUUID();
    localStorage.setItem(PLAYER_KEY, id);
    return id;
  } catch {
    return crypto.randomUUID();
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export function startPlay(): Promise<PlayState> {
  return request("/plays", { method: "POST", body: JSON.stringify({ player_id: playerId() }) });
}

export function sendAnswer(playId: string, step: number, choice: string): Promise<PlayState> {
  return request(`/plays/${playId}/answers`, {
    method: "POST",
    body: JSON.stringify({ step, choice }),
  });
}

export function fetchResult(playId: string): Promise<PlayResult> {
  return request(`/plays/${playId}/result`);
}
