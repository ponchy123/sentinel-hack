#!/bin/bash
echo "Starting Sentinel..."

echo "[1/2] Starting API server on port 8080..."
python -m api.main &
API_PID=$!

echo "[2/2] Starting Dashboard on port 3000..."
cd dashboard
npx vite --host --port 3000 &
DASHBOARD_PID=$!

echo ""
echo "Sentinel is running:"
echo "  Dashboard:  http://localhost:3000"
echo "  API:        http://localhost:8080"
echo "  API Docs:   http://localhost:8080/docs"
echo ""
echo "Press Ctrl+C to stop."

trap "kill $API_PID $DASHBOARD_PID 2>/dev/null" EXIT
wait
