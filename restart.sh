#!/bin/bash
#
# Hammarby Supporterklubb - Server Start/Restart Script
# =====================================================
# This script starts or restarts the Flask development server.
# For production, use the systemd user service instead.
#
# Usage: ./restart.sh [options]
# Options:
#   --port PORT   Port number (default: 5001)
#   --foreground  Run in foreground (no background process)
#   --status      Check if server is running
#   --stop        Stop the server
#   --systemd     Control the systemd user service instead
#   --help        Show this help message
#

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PORT="${PORT:-5001}"
LOG_FILE="/tmp/hammarby-flask.log"
PID_FILE="/tmp/hammarby-flask.pid"
PYTHONPATH="$SCRIPT_DIR"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if venv exists
ensure_venv() {
    if [ ! -d "$SCRIPT_DIR/venv" ]; then
        log_error "Virtual environment not found."
        log_error "Run setup first: ./start.sh"
        exit 1
    fi
}

# Check if server is running (by port)
check_running() {
    if lsof -i :"$PORT" 2>/dev/null | grep -q LISTEN; then
        return 0
    fi

    # Also check PID file
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
    fi

    return 1
}

# Stop the server
stop_server() {
    log_info "Stopping Flask server on port $PORT..."

    # Try to kill by PID file
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            sleep 1
            # Force kill if still running
            kill -9 "$pid" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
    fi

    # Kill any process on the port
    local port_process
    port_process=$(lsof -ti:$PORT 2>/dev/null || true)
    if [ -n "$port_process" ]; then
        log_info "Killing process on port $PORT..."
        kill -9 $port_process 2>/dev/null || true
    fi

    # Kill any Flask process
    pkill -f "python.*backend/app.py" 2>/dev/null || true

    log_success "Server stopped"
}

# Start the server
start_server() {
    local foreground="${1:-false}"

    ensure_venv

    log_info "Starting Flask server on port $PORT..."

    # Ensure directories exist
    mkdir -p "$SCRIPT_DIR/backend/uploads/news"
    mkdir -p "$SCRIPT_DIR/backend/data/news"

    if [ "$foreground" = "true" ]; then
        # Run in foreground
        env PYTHONPATH="$PYTHONPATH" PORT="$PORT" "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/backend/app.py"
    else
        # Run in background
        nohup env PYTHONPATH="$PYTHONPATH" PORT="$PORT" "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/backend/app.py" > "$LOG_FILE" 2>&1 &
        local server_pid=$!
        echo $server_pid > "$PID_FILE"

        log_success "Flask server started (PID: $server_pid)"

        # Wait for server to start
        sleep 2

        # Check if server is running
        if curl -s "http://localhost:$PORT" > /dev/null 2>&1; then
            log_success "Server is running and responding"
            echo ""
            echo "Access the website at:"
            echo "  - http://localhost:$PORT"
            echo "  - http://127.0.0.1:$PORT"
            echo ""
            echo "Logs: $LOG_FILE"
            echo "Stop: $0 --stop"
        else
            log_warning "Server may not be responding yet. Check logs:"
            log_warning "tail -f $LOG_FILE"
        fi
    fi
}

# Show status
show_status() {
    if check_running; then
        log_success "Server is running on port $PORT"
        if [ -f "$PID_FILE" ]; then
            echo "PID: $(cat "$PID_FILE")"
        fi
        echo ""
        echo "Recent logs:"
        tail -10 "$LOG_FILE" 2>/dev/null || echo "No logs available"
    else
        log_warning "Server is not running on port $PORT"
        echo "Start with: $0"
    fi
}

# ---- SYSTEMD CONTROLS ----

systemd_status() {
    log_info "Checking systemd user service status..."
    if systemctl --user is-active hammarby-website.service &> /dev/null; then
        log_success "Systemd service is active"
        systemctl --user status hammarby-website.service --no-pager
    else
        log_warning "Systemd service is not running"
        echo "Start with: $0 --systemd start"
    fi
}

systemd_start() {
    log_info "Starting systemd user service..."
    systemctl --user start hammarby-website.service
    log_success "Service started"
    echo "Status: systemctl --user status hammarby-website"
    echo "Logs:   journalctl --user -u hammarby-website -f"
}

systemd_stop() {
    log_info "Stopping systemd user service..."
    systemctl --user stop hammarby-website.service
    log_success "Service stopped"
}

systemd_restart() {
    log_info "Restarting systemd user service..."
    systemctl --user restart hammarby-website.service
    log_success "Service restarted"
}

# Show usage
show_usage() {
    echo ""
    echo "Hammarby Supporterklubb - Server Control Script"
    echo "================================================"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --port PORT      Port number (default: 5001)"
    echo "  --foreground     Run in foreground (no background process)"
    echo "  --status         Check if server is running"
    echo "  --stop           Stop the server"
    echo "  --restart        Restart the server"
    echo ""
    echo "Systemd user service:"
    echo "  --systemd        Show service status"
    echo "  --systemd start  Start service"
    echo "  --systemd stop   Stop service"
    echo "  --systemd restart  Restart service"
    echo ""
    echo "Examples:"
    echo "  $0                    # Start server on port 5001"
    echo "  $0 --port 8080        # Start server on port 8080"
    echo "  $0 --status           # Check server status"
    echo "  $0 --stop             # Stop the server"
    echo "  $0 --systemd          # Check systemd service"
    echo "  $0 --systemd start    # Start systemd service"
    echo ""
}

# Main function
main() {
    local action="start"
    local foreground="false"
    local systemd_mode=false
    local systemd_action=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --port)
                PORT="$2"
                shift 2
                ;;
            --foreground)
                foreground="true"
                shift
                ;;
            --status)
                action="status"
                shift
                ;;
            --stop)
                action="stop"
                shift
                ;;
            --restart)
                action="restart"
                shift
                ;;
            --systemd)
                systemd_mode=true
                shift
                # Check if next arg is a systemd action
                if [[ $# -gt 0 && "$1" =~ ^(start|stop|restart)$ ]]; then
                    systemd_action="$1"
                    shift
                else
                    systemd_action="status"
                fi
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # Systemd controls
    if [ "$systemd_mode" = true ]; then
        case $systemd_action in
            status)
                systemd_status
                ;;
            start)
                systemd_start
                ;;
            stop)
                systemd_stop
                ;;
            restart)
                systemd_restart
                ;;
        esac
        return
    fi

    # Regular process controls
    case $action in
        start)
            if check_running; then
                log_warning "Server is already running on port $PORT"
                echo "Use '$0 --restart' to restart or '$0 --status' to check status"
                exit 0
            fi
            start_server "$foreground"
            ;;
        stop)
            stop_server
            ;;
        restart)
            stop_server
            sleep 1
            start_server "$foreground"
            ;;
        status)
            show_status
            ;;
    esac
}

# Run main function
main "$@"
