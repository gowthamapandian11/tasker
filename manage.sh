#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/Dockercompose/docker-compose.yml"
COMPOSE_CMD=(docker compose)

echo "$SCRIPT_DIR"
echo "$COMPOSE_FILE"
echo "${COMPOSE_CMD[@]}"

usage() {
  echo "Usage: $0 {start|stop|restart|status|logs}" >&2
  exit 1
}

start_services() {
  echo "Starting services..."
  docker rm -f mongodb logger flask-app >/dev/null 2>&1 || true
  "${COMPOSE_CMD[@]}" -f "$COMPOSE_FILE" down --remove-orphans >/dev/null 2>&1 || true
  "${COMPOSE_CMD[@]}" -f "$COMPOSE_FILE" up -d --build
}

stop_services() {
  echo "Stopping services..."
  "${COMPOSE_CMD[@]}" -f "$COMPOSE_FILE" down
}

restart_services() {
  echo "Restarting services..."
  stop_services
  start_services
}

backup_logs() {
  echo "Backing up logger service logs..."

  local container_name="logger"
  if ! docker ps --format '{{.Names}}' | grep -qx "$container_name"; then
    echo "ERROR: Container '$container_name' is not running." >&2
    exit 1
  fi

  local output_dir="$SCRIPT_DIR/logs-backup"
  mkdir -p "$output_dir"

  local tmp_dir
  tmp_dir=$(mktemp -d)

  echo "Copying /app/logs from container '$container_name'..."
  pushd "$tmp_dir" >/dev/null
  docker cp "$container_name":/app/logs .

  local archive_name="$output_dir/logger-logs.zip"
  zip -r "$archive_name" logs >/dev/null
  popd >/dev/null

  rm -rf "$tmp_dir"
  echo "Logs backed up to: $archive_name"
}

show_status() {
  echo "Service status:"
  "${COMPOSE_CMD[@]}" -f "$COMPOSE_FILE" ps
}

case "${1:-}" in
  start)
    start_services
    ;;
  stop)
    stop_services
    ;;
  restart)
    restart_services
    ;;
  status)
    show_status
    ;;
  logs)
    backup_logs
    ;;
  *)
    usage
    ;;
esac
