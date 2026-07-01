@echo off
echo Starting Sentinel...

echo [1/2] Starting API server on port 8080...
start /B python -m api.main

echo [2/2] Starting Dashboard on port 3000...
cd dashboard
start /B npx vite --host --port 3000

echo.
echo Sentinel is running:
echo   Dashboard:  http://localhost:3000
echo   API:        http://localhost:8080
echo   API Docs:   http://localhost:8080/docs
echo.
echo Press Ctrl+C to stop.
pause
