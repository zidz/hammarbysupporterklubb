#!/bin/bash
#
# Hammarby Supporterklubb - Stop Script
# ======================================
# Stops both the background Flask process and the systemd user service.
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log_info "Stopping Flask server..."

# Try stopping systemd user service
if systemctl --user is-active hammarby-website.service &> /dev/null; then
    log_info "Stopping systemd user service..."
    systemctl --user stop hammarby-website.service
    log_success "Systemd service stopped"
fi

# Find and kill Flask processes
PIDS=$(pgrep -f "python.*backend/app.py" 2>/dev/null || true)

if [ -n "$PIDS" ]; then
    log_info "Found Flask processes: $PIDS"
    kill $PIDS 2>/dev/null || true
    sleep 2

    # Force kill if still running
    PIDS=$(pgrep -f "python.*backend/app.py" 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        log_warning "Force killing remaining processes..."
        kill -9 $PIDS 2>/dev/null || true
    fi

    log_success "Flask server stopped"
else
    log_info "No Flask server processes found"
fi

# Kill any process on port 5000
log_info "Checking for processes on port 5000..."
PORT_PROCESS=$(lsof -ti:5000 2>/dev/null || true)

if [ -n "$PORT_PROCESS" ]; then
    log_warning "Killing process on port 5000: $PORT_PROCESS"
    kill -9 $PORT_PROCESS 2>/dev/null || true
    log_success "Port 5000 freed"
else
    log_info "No processes found on port 5000"
fi

log_success "All servers stopped"
