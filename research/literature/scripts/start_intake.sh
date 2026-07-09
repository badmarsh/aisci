#!/bin/bash
# Start the Literature Intake Daemon

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KILL_SWITCH="$SCRIPT_DIR/../.kill_intake"
PID_FILE="$SCRIPT_DIR/../intake_daemon.pid"
LOG_FILE="$SCRIPT_DIR/../daemon_stdout.log"

if [ -f "$KILL_SWITCH" ]; then
    echo "Removing kill switch at $KILL_SWITCH"
    rm -f "$KILL_SWITCH"
fi

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Intake daemon is already running with PID $PID"
        exit 1
    else
        echo "Stale PID file found, cleaning up."
        rm -f "$PID_FILE"
    fi
fi

echo "Starting Literature Intake Daemon..."
nohup python3 "$SCRIPT_DIR/intake_daemon.py" > "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"
echo "Started with PID $NEW_PID"
echo "Logging output to $LOG_FILE"
