"use client";

import { useState } from "react";
import styles from "./page.module.css";
import { lastKana } from "./kana";
import { mockStats, type NodeStats } from "./mockStats";
import { CHOICES_BY_KANA, MAX_STEPS, START_WORD } from "./routes";

type Answer = {
  fromWord: string;
  choices: string[];
  choice: string;
};

type Phase = "title" | "question" | "result";

function choicesFor(word: string): string[] {
  return CHOICES_BY_KANA[lastKana(word)] ?? [];
}

function rateOf(stats: NodeStats, word: string): number {
  return Math.round((stats.counts[word] / stats.total) * 100);
}

function topOf(stats: NodeStats): string {
  return Object.entries(stats.counts).sort((a, b) => b[1] - a[1])[0][0];
}

export default function Shiritori() {
  const [phase, setPhase] = useState<Phase>("title");
  const [answers, setAnswers] = useState<Answer[]>([]);

  const currentWord = answers.length ? answers[answers.length - 1].choice : START_WORD;
  const step = answers.length + 1;

  const start = () => {
    setAnswers([]);
    setPhase("question");
  };

  const choose = (choice: string) => {
    const next = [...answers, { fromWord: currentWord, choices: choicesFor(currentWord), choice }];
    setAnswers(next);
    if (next.length === MAX_STEPS) setPhase("result");
  };

  return (
    <main className={styles.container}>
      <h1 className={styles.logo}>しりとりんご</h1>

      {phase === "title" && (
        <section className={styles.card}>
          <p className={styles.lead}>
            「りんご」から始まるしりとりを4択で5回。
            <br />
            みんなが一番選んだ答えを当てよう。
          </p>
          <button className={styles.primary} onClick={start}>
            はじめる
          </button>
        </section>
      )}

      {phase === "question" && (
        <section className={styles.card}>
          <p className={styles.step}>
            {step} / {MAX_STEPS}
          </p>
          <ol className={styles.chain}>
            {[START_WORD, ...answers.map((a) => a.choice)].map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ol>
          <p className={styles.current}>{currentWord}</p>
          <p className={styles.prompt}>「{lastKana(currentWord)}」で始まるのは？</p>
          <div className={styles.choices}>
            {choicesFor(currentWord).map((c) => (
              <button key={c} className={styles.choice} onClick={() => choose(c)}>
                {c}
              </button>
            ))}
          </div>
        </section>
      )}

      {phase === "result" && <Result answers={answers} onRetry={start} />}
    </main>
  );
}

function Result({ answers, onRetry }: { answers: Answer[]; onRetry: () => void }) {
  const rows = answers.map((a) => {
    const stats = mockStats(a.fromWord, a.choices);
    return { ...a, stats, top: topOf(stats), rate: rateOf(stats, a.choice) };
  });
  const score = Math.round(rows.reduce((sum, r) => sum + r.rate, 0) / rows.length);
  const hits = rows.filter((r) => r.choice === r.top).length;

  return (
    <section className={styles.card}>
      <p className={styles.scoreLabel}>みんな度</p>
      <p className={styles.score}>{score}%</p>
      <p className={styles.hits}>
        1位と一致: {hits} / {rows.length}
      </p>

      <ol className={styles.steps}>
        {rows.map((r, i) => (
          <li key={i} className={styles.stepRow}>
            <p className={styles.stepHead}>
              {i + 1}. {r.fromWord} → <strong>{r.choice}</strong>
              {r.choice === r.top && <span className={styles.badge}>1位</span>}
            </p>
            {r.choices.map((c) => {
              const rate = rateOf(r.stats, c);
              return (
                <div key={c} className={styles.bar} data-mine={c === r.choice}>
                  <span className={styles.barLabel}>{c}</span>
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

      <p className={styles.note}>※サンプルのため集計はダミー値です。回答は保存されません。</p>
      <button className={styles.primary} onClick={onRetry}>
        もう一度
      </button>
    </section>
  );
}
