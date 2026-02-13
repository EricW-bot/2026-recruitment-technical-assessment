#!/usr/bin/env bash

set -e

TRAP_TRIGGERED=false

# Helper function to kill any process using port 8080
kill_previous_processes() {
  if lsof -i :8080 -t > /dev/null; then
    echo "Killing existing process $(lsof -i :8080 -t) on port 8080..."
    kill -9 $(lsof -i :8080 -t) > /dev/null 2>&1
  fi
}

# Helper function to kill the server and any processes using port 8080
kill_server() {
  if [ "$TRAP_TRIGGERED" = true ]; then
    return
  fi
  TRAP_TRIGGERED=true

  echo "== Stopping the server =="
  deactivate
  if ps -p $SERVER_PID > /dev/null; then
    echo "Killing server with PID: $SERVER_PID"
    kill $SERVER_PID > /dev/null 2>&1
  fi
  kill_previous_processes

}

kill_previous_processes
trap 'kill_server' EXIT ERR

echo "== Starting server =="
python3 -m venv venv > /dev/null 2>&1
source venv/Scripts/activate > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

# Start server in background
python devdonalds.py > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for the server to be up
echo "Waiting for server to start..."
until curl -s http://localhost:8080 > /dev/null; do
  echo -n "."
  sleep 0.05
done
echo
echo "Server is up. Yippee!!"

cd ../autotester

if [ "$1" == "part1" ]; then
  echo "Running test_part1..."
  npm run test_part1
elif [ "$1" == "part2" ]; then
  echo "Running test_part2..."
  npm run test_part2
elif [ "$1" == "part3" ]; then
  echo "Running test_part3..."
  npm run test_part3
else
  # Default: run all tests
  echo "Running all tests..."
  npm run test
fi

kill_server