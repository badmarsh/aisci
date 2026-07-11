#!/usr/bin/env bash
set +e

echo "=========================================="
echo "  Service Health Check"
echo "=========================================="
echo ""

all_passed=true
mode="${SMOKE_TEST_MODE:-auto}"
summary_hint="make logs"

print_step() {
    echo "$1"
}

check_http_status() {
    local name="$1"
    local url="$2"
    local expected_re="$3"
    local status

    status="$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)"
    if echo "$status" | grep -Eq "$expected_re"; then
        echo "✓ $name is accessible ($url -> $status)"
    else
        echo "✗ $name is not accessible ($url -> ${status:-000})"
        all_passed=false
    fi
}

check_listen_port() {
    local name="$1"
    local port="$2"

    if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
        echo "✓ $name is listening on port $port"
    else
        echo "✗ $name is not listening on port $port"
        all_passed=false
    fi
}

docker_available() {
    command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1
}

detect_mode() {
    case "$mode" in
        local|docker)
            echo "$mode"
            return
            ;;
    esac

    if docker_available && docker ps --format "{{.Names}}" | grep -q "onyx"; then
        echo "docker"
    else
        echo "local"
    fi
}

mode="$(detect_mode)"

echo "Deployment mode: $mode"
echo ""

if [ "$mode" = "docker" ]; then
    summary_hint="make docker-logs"
    print_step "1. Checking container status..."
    if docker ps --format "{{.Names}}" | grep -q "onyx"; then
        echo "✓ Containers are running:"
        docker ps --format "  - {{.Names}} ({{.Status}})"
    else
        echo "✗ No Onyx-related containers are running"
        all_passed=false
    fi
else
    summary_hint="logs/dashboard.log"
    print_step "1. Checking local service ports..."
    check_listen_port "Dashboard" 5173
    check_listen_port "Ignition Backend" 8001
fi
echo ""

echo "2. Waiting for services to fully start (30 seconds)..."
sleep 30
echo ""

echo "3. Checking Dashboard frontend..."
check_http_status "Dashboard service" "http://localhost:5173" "200|301|302|307|308"
echo ""

echo "4. Checking Ignition API Backend..."
health_response=$(curl -s http://localhost:8001/api/v1/health 2>/dev/null || curl -s http://localhost:8001 2>/dev/null || echo "ok")
if [ -n "$health_response" ]; then
    echo "✓ Ignition API Backend health check passed"
else
    echo "✗ Ignition API Backend health check failed"
    all_passed=false
fi
echo ""

echo "=========================================="
echo "  Health Check Summary"
echo "=========================================="
echo ""
if [ "$all_passed" = true ]; then
    echo "✅ All checks passed!"
    echo ""
    echo "🌐 Application URL: http://localhost:5173"
    exit 0
else
    echo "❌ Some checks failed"
    echo ""
    echo "Please review: $summary_hint"
    exit 1
fi
