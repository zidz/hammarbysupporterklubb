#!/bin/bash
#
# Hammarby Supporterklubb - Start Script
# ========================================
# This script prepares a new system to run the Hammarby Supporterklubb website.
# Tested on Debian 12 and newer systems.
#
# Usage: ./start.sh [options]
# Options:
#   --demo      Run in demo mode (auto-start server after setup)
#   --help      Show this help message
#
# Author: Hammarby Supporterklubb
# Version: 1.0.0
# Date: 2026-04-08
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
PYTHON_VERSION="3.11"
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

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_warning "This script should be run as root or with sudo privileges"
        log_warning "Some operations may fail without proper permissions"
    fi
}

# Check Python version
check_python() {
    log_info "Checking Python version..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        log_info "Install Python 3 with: apt-get install python3 python3-pip python3-venv"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_info "Found Python ${PYTHON_VERSION}"
    
    # Extract major and minor version numbers
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
    
    MIN_MAJOR=$(echo "$MIN_PYTHON_VERSION" | cut -d'.' -f1)
    MIN_MINOR=$(echo "$MIN_PYTHON_VERSION" | cut -d'.' -f2)
    
    # Compare versions properly
    if [ "$PYTHON_MAJOR" -lt "$MIN_MAJOR" ]; then
        log_error "Python version ${PYTHON_VERSION} is too old. Minimum required: ${MIN_PYTHON_VERSION}"
        exit 1
    elif [ "$PYTHON_MAJOR" -eq "$MIN_MAJOR" ] && [ "$PYTHON_MINOR" -lt "$MIN_MINOR" ]; then
        log_error "Python version ${PYTHON_VERSION} is too old. Minimum required: ${MIN_PYTHON_VERSION}"
        exit 1
    fi
    
    log_success "Python version check passed"
}

# Install system dependencies
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
        "python3-pip"
        "python3-venv"
        "python3-dev"
        "libpq-dev"
        "build-essential"
        "git"
        "curl"
        "wget"
    )
    
    MISSING_PACKAGES=()
    for pkg in "${PACKAGES[@]}"; do
        if ! dpkg -l "$pkg" | grep -q "^ii"; then
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

# Create virtual environment
create_venv() {
    log_info "Creating Python virtual environment..."
    
    if [ -d "$VENV_DIR" ]; then
        log_warning "Virtual environment already exists at $VENV_DIR"
        log_info "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    fi
    
    python3 -m venv "$VENV_DIR"
    log_success "Virtual environment created at $VENV_DIR"
}

# Activate virtual environment
activate_venv() {
    log_info "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    log_success "Virtual environment activated"
}

# Upgrade pip
upgrade_pip() {
    log_info "Upgrading pip..."
    pip install --upgrade pip -q
    log_success "pip upgraded"
}

# Install Python dependencies
install_python_dependencies() {
    log_info "Installing Python dependencies..."
    
    if [ ! -f "${SCRIPT_DIR}/requirements.txt" ]; then
        log_error "requirements.txt not found in ${SCRIPT_DIR}"
        exit 1
    fi
    
    pip install -r "${SCRIPT_DIR}/requirements.txt" -q
    log_success "Python dependencies installed"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p "${SCRIPT_DIR}/backend/uploads/news"
    mkdir -p "${SCRIPT_DIR}/backend/data/news"
    mkdir -p "${SCRIPT_DIR}/screenshots"
    
    log_success "Directories created"
}

# Set proper permissions
set_permissions() {
    log_info "Setting file permissions..."
    
    chmod +x "${SCRIPT_DIR}/start.sh"
    chmod +x "${SCRIPT_DIR}/stop.sh" 2>/dev/null || true
    
    log_success "Permissions set"
}

# Create environment file
create_env_file() {
    log_info "Creating environment file..."
    
    if [ ! -f "${SCRIPT_DIR}/.env" ]; then
        cat > "${SCRIPT_DIR}/.env" << 'EOF'
# Hammarby Supporterklubb - Environment Configuration
# ===================================================
# This file contains environment variables for the application.
# Copy this file to .env.local and customize for your environment.

# Flask Configuration
FLASK_APP=backend/app.py
FLASK_ENV=development
FLASK_DEBUG=1

# Secret Key (CHANGE THIS IN PRODUCTION!)
SECRET_KEY=change-this-secret-key-in-production-use-a-secure-random-string

# Upload Configuration
UPLOAD_FOLDER=./backend/uploads
MAX_CONTENT_LENGTH=104857600  # 100MB in bytes

# Database Configuration (if using database)
# DATABASE_URL=sqlite:///./instance/app.db

# Server Configuration
HOST=0.0.0.0
PORT=5000

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

# Create stop script
create_stop_script() {
    log_info "Creating stop script..."
    
    cat > "${SCRIPT_DIR}/stop.sh" << 'EOF'
#!/bin/bash
#
# Hammarby Supporterklubb - Stop Script
# ======================================
# This script stops the Flask server.
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
EOF
    
    chmod +x "${SCRIPT_DIR}/stop.sh"
    log_success "Stop script created: stop.sh"
}

# Create systemd service file (optional)
create_systemd_service() {
    log_info "Creating systemd service file (optional)..."
    
    cat > "${SCRIPT_DIR}/hammarby-website.service" << 'EOF'
[Unit]
Description=Hammarby Supporterklubb Website
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/hammarby_website
Environment="PATH=/path/to/hammarby_website/venv/bin"
ExecStart=/path/to/hammarby_website/venv/bin/python backend/app.py
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
    
    log_success "Systemd service file created: hammarby-website.service"
    log_warning "Remember to update paths in the service file before using"
}

# Run tests (optional)
run_tests() {
    log_info "Running tests..."
    
    if command -v pytest &> /dev/null; then
        pytest "${SCRIPT_DIR}/tests" -v --tb=short
        log_success "Tests completed"
    else
        log_warning "pytest not found. Install with: pip install pytest"
    fi
}

# Start the server
start_server() {
    log_info "Starting Flask server..."
    
    # Set environment variables
    export FLASK_APP=backend/app.py
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    
    # Start server in background
    cd "$SCRIPT_DIR"
    python backend/app.py &
    
    SERVER_PID=$!
    echo $SERVER_PID > "${SCRIPT_DIR}/.server.pid"
    
    log_success "Flask server started (PID: $SERVER_PID)"
    log_info "Server running at: http://localhost:5000"
    log_info "Stop the server with: ./stop.sh"
    
    # Wait for server to start
    sleep 3
    
    # Check if server is running
    if curl -s http://localhost:5000 > /dev/null 2>&1; then
        log_success "Server is running and responding"
    else
        log_warning "Server may not be responding yet. Check logs for errors."
    fi
}

# Show usage
show_usage() {
    echo ""
    echo "Hammarby Supporterklubb - Start Script"
    echo "======================================="
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --demo      Run in demo mode (auto-start server after setup)"
    echo "  --test      Run tests after setup"
    echo "  --systemd   Create systemd service file"
    echo "  --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Run full setup"
    echo "  $0 --demo       # Setup and start server"
    echo "  $0 --test       # Setup and run tests"
    echo ""
    echo "After setup:"
    echo "  ./start.sh --demo    # Start the server"
    echo "  ./stop.sh            # Stop the server"
    echo ""
}

# Main function
main() {
    echo ""
    echo "========================================"
    echo "  Hammarby Supporterklubb - Setup Script"
    echo "========================================"
    echo ""
    
    # Parse arguments
    DEMO_MODE=false
    RUN_TESTS=false
    CREATE_SYSTEMD=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --demo)
                DEMO_MODE=true
                shift
                ;;
            --test)
                RUN_TESTS=true
                shift
                ;;
            --systemd)
                CREATE_SYSTEMD=true
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
    
    # Run setup steps
    check_root
    check_python
    install_system_dependencies
    create_venv
    activate_venv
    upgrade_pip
    install_python_dependencies
    create_directories
    set_permissions
    create_env_file
    create_stop_script
    
    if [ "$CREATE_SYSTEMD" = true ]; then
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
    
    # Show next steps
    echo "Next steps:"
    echo "  1. Review and customize .env file"
    echo "  2. Start the server: ./start.sh --demo"
    echo "  3. Access the website: http://localhost:5000"
    echo "  4. Stop the server: ./stop.sh"
    echo ""
    
    # Start server in demo mode
    if [ "$DEMO_MODE" = true ]; then
        echo ""
        log_info "Starting server in demo mode..."
        start_server
        echo ""
        log_info "Press Ctrl+C to stop the server"
        wait $SERVER_PID
    fi
}

# Run main function
main "$@"
