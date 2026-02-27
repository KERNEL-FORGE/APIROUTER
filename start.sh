#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "🚀 Starting API ROUTER..."

# Check if virtualenv exists
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "❌ Backend virtualenv not found. Run setup first."
    exit 1
fi

# Start backend
echo "📦 Starting Backend (Django)..."
cd "$BACKEND_DIR"
source venv/bin/activate
python manage.py runserver 8000 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 2

# Start frontend
echo "⚛️ Starting Frontend (React)..."
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ API ROUTER is running!"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo '🛑 Stopped.'; exit 0" SIGINT

wait
