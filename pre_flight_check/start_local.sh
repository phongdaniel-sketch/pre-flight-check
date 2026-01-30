#!/bin/bash

# Kill any existing processes on ports 8000 and 5173
echo "Cleaning up ports..."
lsof -t -i:8000 | xargs kill -9 2>/dev/null
lsof -t -i:5173 | xargs kill -9 2>/dev/null

# Start Backend
echo "Starting Backend..."
npm run backend &
BACKEND_PID=$!

# Wait for backend to be ready (optional, but good practice)
sleep 2

# Start Frontend
echo "Starting Frontend..."
npm run frontend &
FRONTEND_PID=$!

echo "Application started!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Press Ctrl+C to stop both."

# Apply cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

wait
