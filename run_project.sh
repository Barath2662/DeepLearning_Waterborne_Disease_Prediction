#!/usr/bin/env bash
# ============================================================
# run_project.sh – One-click launcher for WaterGuard AI
# Compatible with: Ubuntu, Linux Mint, Fedora, Arch Linux, macOS
# ============================================================

set -e
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   WaterGuard AI – Early Warning System Launcher          ║"
echo "║   Deep Learning Based Water-Borne Disease Prediction     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── 1. Python virtual environment ─────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# ── 2. Install Python dependencies ────────────────────────────
echo "📦 Installing/verifying Python dependencies..."
pip install -q -r "$BACKEND_DIR/requirements.txt"

# ── 3. Train model if not already trained ─────────────────────
MODEL_FILE="$PROJECT_DIR/models/waterborne_model.h5"
if [ ! -f "$MODEL_FILE" ]; then
    echo ""
    echo "🧠 Training Deep Learning model (first run)..."
    echo "   This may take 2-5 minutes..."
    cd "$PROJECT_DIR"
    python train_model.py
    echo "✅ Model training complete!"
else
    echo "✅ Trained model found – skipping training."
fi

# ── 4. Install Node.js frontend dependencies ──────────────────
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo ""
    echo "📦 Installing frontend dependencies (npm install)..."
    cd "$FRONTEND_DIR"
    npm install
fi

# ── 5. Start services ─────────────────────────────────────────
echo ""
echo "🚀 Starting services..."
echo ""

# Start FastAPI backend
echo "  [Backend]  FastAPI  →  http://localhost:8000"
echo "  [API Docs]           →  http://localhost:8000/docs"
cd "$BACKEND_DIR"
source "$VENV_DIR/bin/activate"
uvicorn app:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 2

# Start React frontend
echo "  [Frontend] React    →  http://localhost:5173"
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ✅ WaterGuard AI is running!                            ║"
echo "║                                                          ║"
echo "║  Dashboard : http://localhost:5173                       ║"
echo "║  API       : http://localhost:8000                       ║"
echo "║  API Docs  : http://localhost:8000/docs                  ║"
echo "║                                                          ║"
echo "║  Press Ctrl+C to stop all services                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Wait and cleanup
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait
