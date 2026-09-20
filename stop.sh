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

# Service based on git branch (master = prod, anything else = dev)
BRANCH=$(git -C "$SCRIPT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
if [ "$BRANCH" = "master" ]; then
    SERVICE_NAME="hammarby-website-prod.service"
else
    SERVICE_NAME="hammarby-website-dev.service"
fi

log_info "Stopping Flask server (mode: ${BRANCH:-dev})..."

# Try stopping systemd user service
if systemctl --user is-active "$SERVICE_NAME" &> /dev/null; then
    log_info "Stopping systemd user service: $SERVICE_NAME"
    systemctl --user stop "$SERVICE_NAME"
    log_success "Systemd service stopped"
fi

# Find and kill Flask processes started from this directory (not other clones)
PIDS=$(pgrep -f "python.*${SCRIPT_DIR}/backend/app.py" 2>/dev/null || true)

if [ -n "$PIDS" ]; then
    log_info "Found Flask processes: $PIDS"
    kill $PIDS 2>/dev/null || true
    sleep 2

    # Force kill if still running
    PIDS=$(pgrep -f "python.*${SCRIPT_DIR}/backend/app.py" 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        log_warning "Force killing remaining processes..."
        kill -9 $PIDS 2>/dev/null || true
    fi

    log_success "Flask server stopped"
else
    log_info "No Flask server processes found"
fi

log_success "All servers stopped"
