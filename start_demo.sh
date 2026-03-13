#!/bin/bash
# ============================================
# デモアプリ起動スクリプト
# Backend (FastAPI) と Frontend (Next.js) を同時起動
# ============================================

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

cleanup() {
  echo ""
  echo "サーバーを停止中..."
  kill $PID_BACKEND $PID_FRONTEND 2>/dev/null
  exit 0
}
trap cleanup INT TERM

# Backend 起動
echo "=== Backend (FastAPI) を起動中 ==="
cd "$PROJECT_DIR/backend"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi
.venv/bin/uvicorn main:app --reload --port 8000 &
PID_BACKEND=$!

# Frontend 起動
echo "=== Frontend (Next.js) を起動中 ==="
cd "$PROJECT_DIR/frontend"
if [ ! -d "node_modules" ]; then
  npm install
fi
npm run dev &
PID_FRONTEND=$!

echo ""
echo "=========================================="
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API docs: http://localhost:8000/docs"
echo "=========================================="
echo "  Ctrl+C で両方停止"
echo ""

wait
