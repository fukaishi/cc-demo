# Claude Code 並行開発デモ & ハンズオン

## 対象者

- Cursorで簡単なフロントエンドアプリを作った経験がある方
- ターミナル操作の基本は分かる方

## ゴール

- Claude Codeで「並行開発」がどう動くかを体感する
- Issueドリブンな開発フローを体験する
- 自分の環境で再現できるようになる

---

## Part 1: 実演デモ（25分）

### 1-1. Claude Codeとは（3分）

- ターミナルで動くAIコーディングエージェント
- Cursorとの違い：GUI不要、CLIだけで完結する
- できること：コード生成、ファイル編集、Git操作、テスト実行など

### 1-2. 基本操作デモ（7分）

- `claude` コマンドで起動
- 自然言語で指示 → コードが生成・編集される様子
- ファイル読み取り、検索、編集のライブデモ
- `/help` `/clear` `/compact` など基本コマンド

### 1-3. Issueから始める並行開発デモ（15分）

#### 準備：GitHubにデモ用リポジトリを作成

- シンプルなTodoアプリのリポジトリを用意
- GitHub Issuesに3つのタスクを登録しておく
  - Issue #1: 「Todoの追加機能を実装する」
  - Issue #2: 「Todo一覧のフィルター機能を実装する」
  - Issue #3: 「APIのユニットテストを追加する」

#### デモ本番

1. **Issueの確認**（ターミナルから `gh issue list` で一覧表示）
2. **ターミナルを3タブ開く**
3. 各タブでClaude Codeを起動し、Issueを渡して開発を指示

```
# タブA
gh issue view 1 | claude
→ 「このIssueを実装して。ブランチを切ってコミットまでやって」

# タブB
gh issue view 2 | claude
→ 「このIssueを実装して。ブランチを切ってコミットまでやって」

# タブC
gh issue view 3 | claude
→ 「このIssueのテストを書いて。ブランチを切ってコミットまでやって」
```

4. **3つが同時に進む様子を見せる**
5. 完了後、各ブランチのPRを作成

> ポイント：Cursorだと1ウィンドウで1タスクだが、Claude Codeはターミナルの数だけ並列に動かせる

---

## Part 2: 並行開発の仕組みと環境（20分）

### 2-1. なぜ並行開発できるのか（5分）

- 各ターミナルが独立したClaude Codeセッション
- セッション間でファイルの競合が起きないようにタスクを分ける
- Git Worktreeを使えばブランチごとに完全分離もできる

### 2-2. 並行開発のパターン（10分）

| パターン | やり方 | 向いているケース |
|---|---|---|
| **タブ分割** | ターミナルタブを複数開く | 同じブランチ内で担当ファイルが異なる作業 |
| **tmux/ペイン分割** | tmuxで画面を分割 | 作業状況を一覧しながら進めたい |
| **Git Worktree** | `git worktree add` で作業ディレクトリを分離 | ブランチをまたぐ並行作業、競合リスクを排除したい |
| **バックグラウンド実行** | `claude --background` やサブエージェント | テスト実行など放置できるタスク |

### 2-3. 必要な環境セットアップ（5分）

- **必須**
  - Node.js（v18以上）
  - Claude Codeのインストール：`npm install -g @anthropic-ai/claude-code`
  - Anthropic APIキー or Claude Pro/Maxプラン
- **推奨**
  - tmux（ターミナル分割）
  - Git（Worktree活用のため）
  - 好みのターミナルエミュレータ（iTerm2, Warp, Ghosttyなど）

---

## Part 3: まとめ & 質疑（15分）

### Cursorとの使い分け

| | Cursor | Claude Code |
|---|---|---|
| UI | GUIエディタ | ターミナル |
| 並行作業 | 1ウィンドウ=1タスク | タブの数だけ並列可能 |
| 得意な場面 | UIを見ながらの開発 | 複数タスクの同時進行、CI/CD連携、スクリプト化 |
| 学習コスト | 低い | ターミナル慣れが必要 |

### 次のステップ

- CLAUDE.mdでプロジェクトルールを設定する
- MCPサーバーで外部ツール連携
- フック機能で自動化（保存時にlint実行など）
- スキルでよく使う操作をテンプレート化

---

## 補足A: 有用なMCPサーバー

MCPサーバーを追加すると、Claude Codeから外部サービスを直接操作できるようになる。

| MCP | 概要 | 使いどころ |
|---|---|---|
| **Playwright** | ブラウザ自動操作 | E2Eテスト、スクリーンショット確認、フロントエンドの動作検証 |
| **GitHub** | Issue・PR操作 | `gh` コマンドなしでIssue確認やPR作成をClaude内で完結 |
| **Slack** | メッセージ送受信 | 開発完了の通知、チームへの報告を自動化 |
| **Google Sheets** | スプレッドシート読み書き | テストデータ管理、進捗表の更新 |
| **PostgreSQL / MySQL** | DB直接操作 | スキーマ確認、テストデータ投入、クエリ検証 |
| **Redmine / Linear** | チケット管理 | チケット起点の開発、ステータス更新を自動化 |
| **Figma** | デザインデータ取得 | デザイン仕様を読み取ってコンポーネント生成 |

### MCPの設定方法

```bash
# プロジェクトルートに .mcp.json を作成
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

> 設定ファイルの置き場所：
> - `.mcp.json`（プロジェクト単位）
> - `~/.claude/settings.json`（グローバル）

---

## 補足B: 有用なスキル（スラッシュコマンド）

スキルは `/コマンド名` で呼び出せる再利用可能なプロンプトテンプレート。

| スキル | 概要 |
|---|---|
| **`/simplify`** | 変更したコードの品質・効率をレビューし、問題を修正する |
| **`/claude-api`** | Claude APIやAnthropic SDKを使ったアプリ構築を支援 |
| **`/loop`** | 指定間隔でコマンドを繰り返し実行（例：`/loop 5m /test`） |
| **`/skill-generator`** | テーマを入力するとカスタムスキルを自動生成 |
| **`/plan-generator`** | 技術的な実装計画を自動生成 |
| **`/dev-workflow`** | チケット起点の開発フロー全体（調査→実装→レビュー→MR）を支援 |
| **`/explain-code`** | コードの動作を図解と類比で説明 |

### カスタムスキルの作り方

```bash
# ~/.claude/skills/my-skill/SKILL.md を作成
---
name: my-skill
description: やりたいことの説明
---

スキルの内容（プロンプト）をここに書く
```

> スキルは自分で作れる。チームで共有すれば開発フローを標準化できる。

---

## 参考リンク

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)
- [Claude Code GitHub](https://github.com/anthropics/claude-code)
- [MCP公式サイト](https://modelcontextprotocol.io)
- [MCP Servers一覧（GitHub）](https://github.com/modelcontextprotocol/servers)
