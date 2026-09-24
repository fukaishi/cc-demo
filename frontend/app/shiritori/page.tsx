"use client";

import { useState } from "react";
import styles from "./page.module.css";
import { fetchResult, sendAnswer, startPlay, type PlayResult, type PlayState } from "./api";

type Phase = "title" | "question" | "result";

export default function Shiritori() {
  const [phase, setPhase] = useState<Phase>("title");
  const [play, setPlay] = useState<PlayState | null>(null);
  const [result, setResult] = useState<PlayResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async (task: () => Promise<void>) => {
    setBusy(true);
    setError(null);
    try {
      await task();
    } catch (e) {
      setError(e instanceof TypeError ? "サーバーに接続できません。バックエンドは起動していますか？" : String((e as Error).message));
    } finally {
      setBusy(false);
    }
  };

  const start = () =>
    run(async () => {
      setPlay(await startPlay());
      setResult(null);
      setPhase("question");
    });

  const choose = (choice: string) =>
    run(async () => {
      if (!play) return;
      const next = await sendAnswer(play.play_id, play.step, choice);
      if (next.finished) {
        setResult(await fetchResult(next.play_id));
        setPhase("result");
      }
      setPlay(next);
    });

  return (
    <main className={styles.container}>
      <h1 className={styles.logo}>しりとりんご</h1>

      {error && <p className={styles.error}>{error}</p>}

      {phase === "title" && (
        <section className={styles.card}>
          <p className={styles.lead}>
            「しりとり」から始まるしりとりを4択で5回。
            <br />
            みんなが一番選んだ答えを当てよう。
          </p>
          <button className={styles.primary} onClick={start} disabled={busy}>
            はじめる
          </button>
        </section>
      )}

      {phase === "question" && play && (
        <section className={styles.card}>
          <p className={styles.step}>
            {play.step} / {play.max_steps}
          </p>
          <ol className={styles.chain}>
            {play.history.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ol>
          <p className={styles.current}>{play.word}</p>
          <p className={styles.prompt}>「{play.kana}」で始まるのは？</p>
          <div className={styles.choices}>
            {play.choices.map((c) => (
              <button key={c} className={styles.choice} onClick={() => choose(c)} disabled={busy}>
                {c}
              </button>
            ))}
          </div>
        </section>
      )}

      {phase === "result" && result && <Result result={result} onRetry={start} busy={busy} />}
    </main>
  );
}

function Result({ result, onRetry, busy }: { result: PlayResult; onRetry: () => void; busy: boolean }) {
  return (
    <section className={styles.card}>
      <p className={styles.scoreLabel}>みんな度</p>
      <p className={styles.score}>{result.score}%</p>
      <p className={styles.hits}>
        1位と一致: {result.hits} / {result.steps.length}
      </p>

      <ol className={styles.steps}>
        {result.steps.map((s) => (
          <li key={s.step}>
            <p className={styles.stepHead}>
              {s.step}. {s.from_word} → <strong>{s.choice}</strong>
              {s.is_top && <span className={styles.badge}>1位</span>}
              <span className={styles.total}>{s.total}人</span>
            </p>
            {Object.entries(s.counts).map(([word, count]) => {
              const rate = s.total ? Math.round((count / s.total) * 100) : 0;
              return (
                <div key={word} className={styles.bar} data-mine={word === s.choice}>
                  <span className={styles.barLabel}>{word}</span>
                  <span className={styles.barTrack}>
                    <span className={styles.barFill} style={{ width: `${rate}%` }} />
                  </span>
                  <span className={styles.barRate}>{rate}%</span>
                </div>
              );
            })}
          </li>
        ))}
      </ol>

      <p className={styles.note}>※同じ端末からの回答は、各単語につき最初の1回だけ集計します。</p>
      <button className={styles.primary} onClick={onRetry} disabled={busy}>
        もう一度
      </button>
    </section>
  );
}
