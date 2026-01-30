#!/bin/bash
echo "Starting debug session..." > debug.log

# Kill existing
echo "Killing old processes..." >> debug.log
lsof -t -i:8000 | xargs kill -9 2>/dev/null
lsof -t -i:5173 | xargs kill -9 2>/dev/null

# Start Backend
echo "Starting Backend..." >> debug.log
cd api
export PORT=8000
nohup node server.js > ../backend_debug.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID" >> ../debug.log
cd ..

# Start Frontend
echo "Starting Frontend..." >> debug.log
cd frontend
nohup npm run dev -- --host > ../frontend_debug.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID" >> ../debug.log
cd ..

echo "Services started. Check backend_debug.log and frontend_debug.log"
