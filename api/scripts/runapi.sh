#!/usr/bin/env bash
# Simple runner for flat.py runapi with pidfile handling.

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
cd "$PROJECT_ROOT"

DEFAULT_PY_BIN="$PROJECT_ROOT/.venv/bin/python"
if [ -x "$DEFAULT_PY_BIN" ]; then
  PYTHON_BIN="${PYTHON_BIN:-$DEFAULT_PY_BIN}"
else
  PYTHON_BIN="${PYTHON_BIN:-python}"
fi
PORT="${PORT:-39991}"
PIDFILE="${PIDFILE:-$PROJECT_ROOT/runapi.pid}"
LOGFILE="${LOGFILE:-$PROJECT_ROOT/logs/runapi.log}"

mkdir -p "$(dirname "$LOGFILE")"

is_running() {
  local pid_file="$1"
  if [ -f "$pid_file" ]; then
    local pid
    pid="$(cat "$pid_file")"
    if ps -p "$pid" > /dev/null 2>&1; then
      return 0
    fi
  fi
  return 1
}

start() {
  if is_running "$PIDFILE"; then
    echo "runapi already running (pid $(cat "$PIDFILE"))"
    exit 0
  fi
  echo "Starting runapi on port $PORT"
  nohup "$PYTHON_BIN" flat.py runapi --port "$PORT" > "$LOGFILE" 2>&1 &
  echo $! > "$PIDFILE"
}

stop() {
  if is_running "$PIDFILE"; then
    local pid
    pid="$(cat "$PIDFILE")"
    echo "Stopping runapi (pid $pid)"
    kill "$pid" || true
    sleep 1
    if ps -p "$pid" > /dev/null 2>&1; then
      echo "Force killing runapi"
      kill -9 "$pid" || true
    fi
    rm -f "$PIDFILE"
  else
    echo "runapi not running"
    rm -f "$PIDFILE" 2>/dev/null || true
  fi
}

status() {
  if is_running "$PIDFILE"; then
    echo "runapi running (pid $(cat "$PIDFILE")) on port $PORT"
  else
    echo "runapi not running"
  fi
}

case "${1:-}" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  restart)
    stop
    start
    ;;
  status)
    status
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status}"
    exit 1
    ;;
esac

exit 0
