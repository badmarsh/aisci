#!/usr/bin/env bash
# dev.sh - Run frontend (Next.js)
# Ctrl+C stops both process groups and frees port 3000.

set -m  # job control: each background job gets its own process group

ROOT="$(cd "$(dirname "$0")" && pwd)"
PIDS=()

cleanup() {
    trap - INT TERM EXIT
    echo
    echo "[dev] Stopping servers..."

    for pid in "${PIDS[@]}"; do
        # Negative pid = whole process group (npm -> node -> next dev, etc.)
        kill -TERM -"$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
    done

    sleep 1

    for pid in "${PIDS[@]}"; do
        kill -KILL -"$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null || true
    done

    # Belt-and-suspenders: free the ports if anything is still listening.
    for port in 3000; do
        if command -v lsof >/dev/null 2>&1; then
            pids=$(lsof -ti tcp:"$port" 2>/dev/null || true)
            [ -n "$pids" ] && kill -KILL $pids 2>/dev/null || true
        elif command -v fuser >/dev/null 2>&1; then
            fuser -k "${port}/tcp" 2>/dev/null || true
        fi
    done

    echo "[dev] Stopped."
}

trap cleanup INT TERM EXIT

echo "[dev] Starting frontend (Next.js on :3000)..."
(
    cd "$ROOT"
    exec npm run dev
) &
PIDS+=($!)

echo
echo "[dev]  Frontend  http://localhost:3000"
echo "[dev]  Ctrl+C to stop."
echo

# Wait for either to exit; the EXIT trap then tears down the rest.
wait -n
