#!/bin/bash
#
# Hammarby Supporterklubb - Server Start/Restart Script
# =====================================================
# This script starts or restarts the Flask development server.
#
# Usage: ./restart.sh [options]
# Options:
#   --port PORT   Port number (default: 5001)
#   --foreground  Run in foreground (no background process)
#   --status      Check if server is running
#   --stop        Stop the server
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

# Check if server is running
check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            return 0
        fi
    fi
    
    # Also check by port
    if lsof -i :"$PORT" 2>/dev/null | grep -q LISTEN; then
        return 0
    fi
    
    return 1
}

# Stop the server
stop_server() {
    log_info "Stopping Flask server..."
    
    # Try to kill by PID file
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID" 2>/dev/null || true
            sleep 1
            # Force kill if still running
            kill -9 "$PID" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
    fi
    
    # Kill any process on the port
    PORT_PROCESS=$(lsof -ti:$PORT 2>/dev/null || true)
    if [ -n "$PORT_PROCESS" ]; then
        log_info "Killing process on port $PORT..."
        kill -9 $PORT_PROCESS 2>/dev/null || true
    fi
    
    # Kill any Flask process
    pkill -f "python.*backend/app.py" 2>/dev/null || true
    
    log_success "Server stopped"
}

# Start the server
start_server() {
    FOREGROUND="${1:-false}"
    
    log_info "Starting Flask server on port $PORT..."
    
    # Ensure directories exist
    mkdir -p "$SCRIPT_DIR/backend/uploads/news"
    mkdir -p "$SCRIPT_DIR/backend/data/news"
    
    # Check if venv exists
    if [ ! -d "$SCRIPT_DIR/venv" ]; then
        log_error "Virtual environment not found. Running: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        python3 -m venv "$SCRIPT_DIR/venv"
        source "$SCRIPT_DIR/venv/bin/activate"
        pip install -r "$SCRIPT_DIR/requirements.txt" -q
        log_success "Virtual environment created and dependencies installed"
    fi
    
    if [ "$FOREGROUND" = "true" ]; then
        # Run in foreground
        env PYTHONPATH="$PYTHONPATH" PORT="$PORT" "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/backend/app.py"
    else
        # Run in background
        nohup env PYTHONPATH="$PYTHONPATH" PORT="$PORT" "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/backend/app.py" > "$LOG_FILE" 2>&1 &
        SERVER_PID=$!
        echo $SERVER_PID > "$PID_FILE"
        
        log_success "Flask server started (PID: $SERVER_PID)"
        
        # Wait for server to start
        sleep 2
        
        # Check if server is running
        if curl -s http://localhost:$PORT > /dev/null 2>&1; then
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
        log_success "Server is running"
        if [ -f "$PID_FILE" ]; then
            echo "PID: $(cat "$PID_FILE")"
        fi
        echo "Port: $PORT"
        echo "Logs: $LOG_FILE"
        echo ""
        echo "Recent logs:"
        tail -10 "$LOG_FILE" 2>/dev/null || echo "No logs available"
    else
        log_warning "Server is not running"
        echo "Start with: $0"
    fi
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
    echo "  --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Start server on port 5001"
    echo "  $0 --port 8080  # Start server on port 8080"
    echo "  $0 --status     # Check server status"
    echo "  $0 --stop       # Stop the server"
    echo "  $0 --restart    # Restart the server"
    echo ""
}

# Main function
main() {
    ACTION="start"
    FOREGROUND="false"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --port)
                PORT="$2"
                shift 2
                ;;
            --foreground)
                FOREGROUND="true"
                shift
                ;;
            --status)
                ACTION="status"
                shift
                ;;
            --stop)
                ACTION="stop"
                shift
                ;;
            --restart)
                ACTION="restart"
                shift
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
    
    case $ACTION in
        start)
            if check_running; then
                log_warning "Server is already running"
                echo "Use '$0 --restart' to restart or '$0 --status' to check status"
                exit 0
            fi
            start_server "$FOREGROUND"
            ;;
        stop)
            stop_server
            ;;
        restart)
            stop_server
            sleep 1
            start_server "$FOREGROUND"
            ;;
        status)
            show_status
            ;;
    esac
}

# Run main function
main "$@"
