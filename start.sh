#!/bin/bash
#
# Hammarby Supporterklubb - Setup Script
# ========================================
# This script prepares a new system to run the Hammarby Supporterklubb website.
# Tested on Debian 12 and newer systems.
#
# Two-phase setup:
#   1. sudo ./start.sh --init    (root: installs system packages)
#   2. ./start.sh                (user: creates venv, installs pip deps)
#
# Usage: ./start.sh [options]
# Options:
#   --init        Root-only: install system packages (run with sudo)
#   --demo        Run in demo mode (auto-start server after setup)
#   --test        Run tests after setup
#   --systemd     Install systemd user service
#   --help        Show this help message
#
# Author: Hammarby Supporterklubb
# Version: 2.0.0
# Date: 2026-08-10
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuration
VENV_DIR="${SCRIPT_DIR}/venv"
MIN_PYTHON_VERSION="3.9"

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

# ---- ROOT-ONLY FUNCTIONS (init mode) ----

# Check if running as root
require_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This operation requires root privileges"
        log_error "Run with: sudo $0 --init"
        exit 1
    fi
}

# Check if running as regular user (NOT root)
require_user() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This operation must NOT be run as root"
        log_error "Run as your regular user (without sudo)"
        log_error "Only --init mode should use sudo"
        exit 1
    fi
}

# Install system dependencies (requires root)
install_system_dependencies() {
    log_info "Checking system dependencies..."

    # Check if apt is available
    if ! command -v apt-get &> /dev/null; then
        log_warning "apt-get not found. This script is designed for Debian/Ubuntu systems"
        return
    fi

    # Update package list
    log_info "Updating package list..."
    apt-get update -qq

    # Check and install required packages
    PACKAGES=(
        "python3"
        "python3-venv"
        "python3-dev"
        "build-essential"
    )

    MISSING_PACKAGES=()
    for pkg in "${PACKAGES[@]}"; do
        if ! dpkg -l "$pkg" 2>/dev/null | grep -q "^ii"; then
            MISSING_PACKAGES+=("$pkg")
        fi
    done

    if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
        log_info "Installing missing system packages: ${MISSING_PACKAGES[*]}"
        apt-get install -y -qq "${MISSING_PACKAGES[@]}"
        log_success "System packages installed"
    else
        log_success "All system packages are already installed"
    fi
}

# ---- USER FUNCTIONS (default mode) ----

# Check Python version
check_python() {
    log_info "Checking Python version..."

    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        log_error "Run system init first: sudo $0 --init"
        exit 1
    fi

    local pyver
    pyver=$(python3 --version | cut -d' ' -f2)
    log_info "Found Python ${pyver}"

    # Extract major and minor version numbers
    local py_major py_minor
    py_major=$(echo "$pyver" | cut -d'.' -f1)
    py_minor=$(echo "$pyver" | cut -d'.' -f2)

    local min_major min_minor
    min_major=$(echo "$MIN_PYTHON_VERSION" | cut -d'.' -f1)
    min_minor=$(echo "$MIN_PYTHON_VERSION" | cut -d'.' -f2)

    # Compare versions properly
    if [ "$py_major" -lt "$min_major" ]; then
        log_error "Python version ${pyver} is too old. Minimum required: ${MIN_PYTHON_VERSION}"
        exit 1
    elif [ "$py_major" -eq "$min_major" ] && [ "$py_minor" -lt "$min_minor" ]; then
        log_error "Python version ${pyver} is too old. Minimum required: ${MIN_PYTHON_VERSION}"
        exit 1
    fi

    log_success "Python version check passed"
}

# Create virtual environment
create_venv() {
    log_info "Creating Python virtual environment..."

    if [ -d "$VENV_DIR" ]; then
        log_info "Virtual environment already exists at $VENV_DIR"
    else
        python3 -m venv "$VENV_DIR"
        log_success "Virtual environment created"
    fi
}

# Install Python dependencies
install_python_dependencies() {
    log_info "Installing Python dependencies..."

    if [ ! -f "${SCRIPT_DIR}/requirements.txt" ]; then
        log_error "requirements.txt not found in ${SCRIPT_DIR}"
        exit 1
    fi

    "${VENV_DIR}/bin/pip" install --upgrade pip -q
    "${VENV_DIR}/bin/pip" install -r "${SCRIPT_DIR}/requirements.txt" -q
    log_success "Python dependencies installed"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."

    mkdir -p "${SCRIPT_DIR}/backend/uploads/news"
    mkdir -p "${SCRIPT_DIR}/backend/data/news"

    log_success "Directories created"
}

# Set proper permissions
set_permissions() {
    log_info "Setting file permissions..."

    chmod +x "${SCRIPT_DIR}/start.sh"
    chmod +x "${SCRIPT_DIR}/stop.sh" 2>/dev/null || true
    chmod +x "${SCRIPT_DIR}/restart.sh" 2>/dev/null || true

    log_success "Permissions set"
}

# Create environment file
create_env_file() {
    log_info "Checking environment file..."

    if [ ! -f "${SCRIPT_DIR}/.env" ]; then
        cat > "${SCRIPT_DIR}/.env" << 'EOF'
# Hammarby Supporterklubb - Environment Configuration
# ===================================================
# This file contains environment variables for the application.

# Flask Configuration
FLASK_APP=backend/app.py
FLASK_ENV=development
FLASK_DEBUG=1

# Secret Key (CHANGE THIS IN PRODUCTION!)
SECRET_KEY=change-this-secret-key-in-production-use-a-secure-random-string

# Upload Configuration
UPLOAD_FOLDER=./backend/uploads
MAX_CONTENT_LENGTH=104857600  # 100MB in bytes

# Server Configuration
HOST=0.0.0.0
PORT=5050

# HAProxy/Proxy Configuration
PROXY_FIX=True
PROXY_FIX_X_FOR=1
PROXY_FIX_X_PROTO=1
PROXY_FIX_X_HOST=1
PROXY_FIX_X_PREFIX=1
EOF
        log_success "Environment file created: .env"
        log_warning "Remember to customize .env for your environment"
    else
        log_info "Environment file already exists"
    fi
}

# ---- STOP SCRIPT ----

# Create stop script
create_stop_script() {
    log_info "Creating stop script..."

    cat > "${SCRIPT_DIR}/stop.sh" << 'STOPEOF'
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
STOPEOF

    chmod +x "${SCRIPT_DIR}/stop.sh"
    log_success "Stop script created: stop.sh"
}

# ---- SYSTEMD SERVICE ----

# Create systemd user service file
create_systemd_service() {
    log_info "Creating systemd user service..."

    local service_name="hammarby-website.service"
    local user_service_dir="$HOME/.config/systemd/user"
    local current_user
    current_user=$(whoami)

    # Create systemd user directory if it doesn't exist
    mkdir -p "$user_service_dir"

    cat > "${user_service_dir}/${service_name}" << SVCEOF
[Unit]
Description=Hammarby Supporterklubb Website
After=network.target

[Service]
Type=simple
WorkingDirectory=${SCRIPT_DIR}
Environment="PATH=${VENV_DIR}/bin:${PATH}"
Environment="PYTHONPATH=${SCRIPT_DIR}"
Environment="PORT=5000"
ExecStart=${VENV_DIR}/bin/python ${SCRIPT_DIR}/backend/app.py
Restart=on-failure
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=hammarby-website

[Install]
WantedBy=default.target
SVCEOF

    # Reload systemd user daemon
    systemctl --user daemon-reload

    # Enable the service
    systemctl --user enable hammarby-website.service

    log_success "Systemd user service installed: ${service_name}"
    log_info "Start with: systemctl --user start hammarby-website"
    log_info "Status:      systemctl --user status hammarby-website"
    log_info "Logs:        journalctl --user -u hammarby-website -f"
}

# ---- RUN SERVER ----

# Start the server (demo/dev mode)
start_server() {
    log_info "Starting Flask server..."

    # Source env file if it exists
    if [ -f "${SCRIPT_DIR}/.env" ]; then
        set -a
        # shellcheck disable=SC1091
        source "${SCRIPT_DIR}/.env"
        set +a
    fi

    export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
    export PORT="${PORT:-5000}"

    # Start server in background
    nohup "${VENV_DIR}/bin/python" "${SCRIPT_DIR}/backend/app.py" > "/tmp/hammarby-flask.log" 2>&1 &
    SERVER_PID=$!
    echo $SERVER_PID > "${SCRIPT_DIR}/.server.pid"

    log_success "Flask server started (PID: $SERVER_PID)"
    log_info "Server running at: http://localhost:${PORT:-5000}"
    log_info "Logs: /tmp/hammarby-flask.log"
    log_info "Stop the server with: ./stop.sh"

    # Wait for server to start
    sleep 3

    # Check if server is running
    if curl -s "http://localhost:${PORT:-5000}" > /dev/null 2>&1; then
        log_success "Server is running and responding"
    else
        log_warning "Server may not be responding yet. Check logs:"
        log_warning "tail -f /tmp/hammarby-flask.log"
    fi
}

# Run tests
run_tests() {
    log_info "Running tests..."

    "${VENV_DIR}/bin/python" -m pytest "${SCRIPT_DIR}/tests" -v --tb=short
    log_success "Tests completed"
}

# Show usage
show_usage() {
    echo ""
    echo "Hammarby Supporterklubb - Setup Script"
    echo "======================================="
    echo ""
    echo "Usage:"
    echo "  sudo ./start.sh --init      System init (requires root)"
    echo "  ./start.sh                  User setup (venv, pip deps)"
    echo ""
    echo "Options:"
    echo "  --init        Root-only: install system packages (run with sudo)"
    echo "  --demo        Run in demo mode (auto-start server after setup)"
    echo "  --test        Run tests after setup"
    echo "  --systemd     Install systemd user service"
    echo "  --help        Show this help message"
    echo ""
    echo "First-time setup (2 steps):"
    echo "  1. sudo ./start.sh --init     # Install system packages"
    echo "  2. ./start.sh                 # Create venv + pip packages"
    echo ""
    echo "Running the server:"
    echo "  ./start.sh --demo                    # Dev server (background)"
    echo "  ./restart.sh                         # Dev server (port 5001)"
    echo "  systemctl --user start hammarby-website  # Production (systemd)"
    echo ""
    echo "Stopping the server:"
    echo "  ./stop.sh"
    echo ""
}

# ---- INIT MODE (root) ----

main_init() {
    require_root

    echo ""
    echo "========================================"
    echo "  Hammarby Supporterklubb - System Init"
    echo "  (Running as root)"
    echo "========================================"
    echo ""

    install_system_dependencies

    echo ""
    log_success "========================================"
    log_success "  System initialization complete!"
    log_success "========================================"
    echo ""
    log_info "Next step (run as regular user):"
    log_info "  ./start.sh"
    echo ""
}

# ---- MAIN (user) ----

main() {
    # Parse arguments
    INIT_MODE=false
    DEMO_MODE=false
    RUN_TESTS=false
    INSTALL_SYSTEMD=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --init)
                INIT_MODE=true
                shift
                ;;
            --demo)
                DEMO_MODE=true
                shift
                ;;
            --test)
                RUN_TESTS=true
                shift
                ;;
            --systemd)
                INSTALL_SYSTEMD=true
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

    # Init mode runs as root
    if [ "$INIT_MODE" = true ]; then
        main_init
        return
    fi

    # All other modes require regular user
    require_user

    echo ""
    echo "========================================"
    echo "  Hammarby Supporterklubb - Setup Script"
    echo "  (Running as: $(whoami))"
    echo "========================================"
    echo ""

    # Run setup steps
    check_python
    create_venv
    install_python_dependencies
    create_directories
    set_permissions
    create_env_file
    create_stop_script

    if [ "$INSTALL_SYSTEMD" = true ]; then
        create_systemd_service
    fi

    if [ "$RUN_TESTS" = true ]; then
        run_tests
    fi

    echo ""
    log_success "========================================"
    log_success "  Setup completed successfully!"
    log_success "========================================"
    echo ""
    echo "Next steps:"
    echo "  1. Review and customize .env file"
    echo "  2. Start dev server: ./start.sh --demo"
    echo "  3. Or start systemd: systemctl --user start hammarby-website"
    echo "  4. Access: http://localhost:5000"
    echo ""

    # Start server in demo mode
    if [ "$DEMO_MODE" = true ]; then
        echo ""
        log_info "Starting server in demo mode..."
        start_server
        echo ""
        log_info "Press Ctrl+C to stop, or run: ./stop.sh"
        wait $SERVER_PID 2>/dev/null || true
    fi
}

# Run main function
main "$@"
