#!/bin/bash
set -e

logfile=/log/start.log
mkdir -p /log

ts() {
  date +"%Y-%m-%d %H:%M:%S"
}

is_true() {
  value="$(echo "${1:-false}" | tr '[:upper:]' '[:lower:]')"
  case "$value" in
    true|1|yes|y|on) return 0 ;;
    *) return 1 ;;
  esac
}

APP_MODULE="${APP_MODULE:-app.main:app}"
APP_HOST="${APP_HOST:-0.0.0.0}"
PORT="${PORT:-8080}"
LOG_LEVEL="${LOG_LEVEL:-info}"
DEBUG_BIND="${DEBUG_BIND:-0.0.0.0}"
DEBUG_PORT="${DEBUG_PORT:-5080}"
UVICORN_WORKERS="${UVICORN_WORKERS:-1}"
UVICORN_RELOAD="${UVICORN_RELOAD:-false}"

uvicorn_args=("$APP_MODULE" "--host" "$APP_HOST" "--port" "$PORT" "--proxy-headers" "--log-level" "$LOG_LEVEL")

if is_true "$UVICORN_RELOAD"; then
  uvicorn_args+=("--reload")
elif ! is_true "${debug:-${DEBUG:-false}}" && [ "$UVICORN_WORKERS" != "1" ]; then
  uvicorn_args+=("--workers" "$UVICORN_WORKERS")
fi

if is_true "${debug:-${DEBUG:-false}}"; then
  debugpy_args=("-m" "debugpy" "--listen" "${DEBUG_BIND}:${DEBUG_PORT}")

  if is_true "${DEBUG_SUSPEND:-false}"; then
    touch /tmp/debugpy-waiting
    echo "$(ts) : starting ${APP_MODULE} with debugpy on ${DEBUG_BIND}:${DEBUG_PORT}, waiting for debugger" | tee -a "$logfile"
    debugpy_args+=("--wait-for-client")
  else
    rm -f /tmp/debugpy-waiting
    echo "$(ts) : starting ${APP_MODULE} with debugpy on ${DEBUG_BIND}:${DEBUG_PORT}" | tee -a "$logfile"
  fi

  exec python "${debugpy_args[@]}" -m uvicorn "${uvicorn_args[@]}"
else
  rm -f /tmp/debugpy-waiting
  echo "$(ts) : starting ${APP_MODULE} without debugger" | tee -a "$logfile"
  exec uvicorn "${uvicorn_args[@]}"
fi
