#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PROXY_SCRIPT="$SCRIPT_DIR/cdp-proxy.mjs"
PROXY_PID_FILE="/tmp/cdp-proxy.pid"
PROXY_PORT=3456

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Node.js version
check_node() {
    log_info "Checking Node.js..."

    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed"
        echo ""
        echo "Please install Node.js 22+ from https://nodejs.org/"
        exit 1
    fi

    NODE_VERSION=$(node -v | sed 's/v//')
    NODE_MAJOR=$(echo "$NODE_VERSION" | cut -d. -f1)

    if [ "$NODE_MAJOR" -lt 22 ]; then
        log_warn "Node.js version is $NODE_VERSION (recommended: 22+)"
        log_info "You can continue, but for best experience, upgrade to Node.js 22+"
    else
        log_info "Node.js version: $NODE_VERSION ✓"
    fi
}

# Check Chrome debugging port
check_chrome() {
    log_info "Checking Chrome remote debugging..."

    # Check if Chrome is listening on the debugging port
    if curl -s --connect-timeout 2 "http://localhost:9222/json/version" > /dev/null 2>&1; then
        log_info "Chrome remote debugging is enabled on port 9222 ✓"
        return 0
    fi

    # Check if Proxy is already running
    if curl -s --connect-timeout 2 "http://localhost:$PROXY_PORT/health" > /dev/null 2>&1; then
        log_info "CDP Proxy is already running ✓"
        return 0
    fi

    log_error "Chrome remote debugging is not enabled"
    echo ""
    echo "Please enable Chrome remote debugging:"
    echo "1. Open Chrome and go to: chrome://inspect/#remote-debugging"
    echo "2. Check 'Allow remote debugging for this browser instance'"
    echo "3. Restart Chrome if needed"
    echo ""
    echo "Alternatively, start Chrome with debugging enabled:"
    echo "  chrome --remote-debugging-port=9222"
    echo ""

    exit 1
}

# Ensure proxy is running
ensure_proxy() {
    log_info "Checking CDP Proxy..."

    # Check if proxy is already running
    if curl -s --connect-timeout 2 "http://localhost:$PROXY_PORT/health" > /dev/null 2>&1; then
        log_info "CDP Proxy is already running on port $PROXY_PORT ✓"
        return 0
    fi

    # Check if proxy script exists
    if [ ! -f "$PROXY_SCRIPT" ]; then
        log_error "CDP Proxy script not found at: $PROXY_SCRIPT"
        exit 1
    fi

    log_info "Starting CDP Proxy..."

    # Start the proxy in background
    node "$PROXY_SCRIPT" &
    PROXY_PID=$!

    echo "$PROXY_PID" > "$PROXY_PID_FILE"

    # Wait for proxy to be ready
    log_info "Waiting for CDP Proxy to start..."
    for i in {1..30}; do
        if curl -s --connect-timeout 1 "http://localhost:$PROXY_PORT/health" > /dev/null 2>&1; then
            log_info "CDP Proxy started successfully (PID: $PROXY_PID) ✓"
            return 0
        fi
        sleep 1
    done

    log_error "Failed to start CDP Proxy"
    exit 1
}

# Main execution
main() {
    echo "========================================"
    echo "  web-access Skill - Dependencies Check"
    echo "========================================"
    echo ""

    check_node
    check_chrome
    ensure_proxy

    echo ""
    echo "========================================"
    echo "  All checks passed! Ready to use CDP."
    echo "========================================"
}

main "$@"
