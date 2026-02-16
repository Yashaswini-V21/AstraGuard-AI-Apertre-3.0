#!/usr/bin/env bash
#
# AstraGuard AI Local Development Setup Script (Bash)
#
# Automated setup script for AstraGuard AI development environment on Linux/macOS.
# Checks prerequisites, installs dependencies, and configures the local environment.
#
# Usage:
#   ./setup-dev.sh [OPTIONS]
#
# Options:
#   --skip-tests    Skip running initial tests after setup
#   --skip-ui       Skip UI/frontend setup
#   --force         Force reinstallation even if already set up
#   --help          Show this help message
#

set -e  # Exit on error

# Script configuration
SCRIPT_VERSION="1.0.0"
MIN_PYTHON_VERSION="3.9"
MIN_NODE_VERSION="16.0"
MIN_GIT_VERSION="2.30"

# Parse arguments
SKIP_TESTS=false
SKIP_UI=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-ui)
            SKIP_UI=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --help)
            sed -n '2,14p' "$0" | sed 's/^# //'
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Color output functions
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_step() { echo -e "\n${MAGENTA}🔧 $1${NC}"; }

# Banner
show_banner() {
    echo -e "${CYAN}"
    cat << "EOF"

╔═══════════════════════════════════════════════════════╗
║                                                       ║
║           AstraGuard AI Setup Script v1.0.0          ║
║     Automated Local Development Environment Setup    ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝

EOF
    echo -e "${NC}"
}

# Version comparison
version_compare() {
    local current=$1
    local required=$2
    
    # Use sort -V for version comparison
    if printf '%s\n%s\n' "$required" "$current" | sort -V -C; then
        return 0  # current >= required
    else
        return 1  # current < required
    fi
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking Prerequisites"
    
    local prerequisites_met=true
    
    # Check Python
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version 2>&1 | awk '{print $2}')
        if version_compare "$python_version" "$MIN_PYTHON_VERSION"; then
            log_success "Python $python_version (>= $MIN_PYTHON_VERSION required)"
        else
            log_error "Python version $python_version is below minimum $MIN_PYTHON_VERSION"
            prerequisites_met=false
        fi
    elif command -v python &> /dev/null; then
        local python_version=$(python --version 2>&1 | awk '{print $2}')
        if version_compare "$python_version" "$MIN_PYTHON_VERSION"; then
            log_success "Python $python_version (>= $MIN_PYTHON_VERSION required)"
        else
            log_error "Python version $python_version is below minimum $MIN_PYTHON_VERSION"
            prerequisites_met=false
        fi
    else
        log_error "Python not found. Please install Python $MIN_PYTHON_VERSION or higher"
        prerequisites_met=false
    fi
    
    # Set python command
    if command -v python3 &> /dev/null; then
        PYTHON_CMD=python3
        PIP_CMD=pip3
    else
        PYTHON_CMD=python
        PIP_CMD=pip
    fi
    
    # Check pip
    if command -v $PIP_CMD &> /dev/null; then
        local pip_version=$($PIP_CMD --version 2>&1 | awk '{print $2}')
        log_success "pip $pip_version installed"
    else
        log_error "pip not found. Please install pip"
        prerequisites_met=false
    fi
    
    # Check Node.js
    if [ "$SKIP_UI" = false ]; then
        if command -v node &> /dev/null; then
            local node_version=$(node --version 2>&1 | sed 's/v//')
            if version_compare "$node_version" "$MIN_NODE_VERSION"; then
                log_success "Node.js $node_version (>= $MIN_NODE_VERSION required)"
            else
                log_warning "Node.js version $node_version is below recommended $MIN_NODE_VERSION"
            fi
        else
            log_warning "Node.js not found. UI setup will be skipped"
            SKIP_UI=true
        fi
        
        # Check npm
        if command -v npm &> /dev/null; then
            local npm_version=$(npm --version 2>&1)
            log_success "npm $npm_version installed"
        else
            log_warning "npm not found"
        fi
    fi
    
    # Check Git
    if command -v git &> /dev/null; then
        local git_version=$(git --version 2>&1 | awk '{print $3}')
        log_success "Git $git_version installed"
    else
        log_warning "Git not found. Some features may not work"
    fi
    
    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        local docker_version=$(docker --version 2>&1 | awk '{print $3}' | sed 's/,//')
        log_success "Docker $docker_version installed (optional)"
    else
        log_info "Docker not found (optional for containerized deployment)"
    fi
    
    if [ "$prerequisites_met" = false ]; then
        log_error "Prerequisites not met. Please install required software and try again."
        exit 1
    fi
    
    log_success "All prerequisites met!"
}

# Setup Python environment
setup_python_environment() {
    log_step "Setting Up Python Environment"
    
    # Check if venv already exists
    if [ -d "venv" ] && [ "$FORCE" = false ]; then
        log_warning "Virtual environment already exists. Use --force to recreate."
        log_info "Activating existing environment..."
    else
        if [ -d "venv" ]; then
            log_info "Removing existing virtual environment..."
            rm -rf venv
        fi
        
        log_info "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
        log_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    source venv/bin/activate
    log_success "Virtual environment activated"
    
    # Upgrade pip
    log_info "Upgrading pip..."
    $PYTHON_CMD -m pip install --upgrade pip --quiet
    log_success "pip upgraded"
    
    # Install dependencies
    log_info "Installing Python dependencies from Requirements.txt..."
    pip install -r Requirements.txt --quiet
    log_success "Python dependencies installed"
    
    # Install development dependencies if available
    if [ -f "src/config/requirements-dev.txt" ]; then
        log_info "Installing development dependencies..."
        pip install -r src/config/requirements-dev.txt --quiet
        log_success "Development dependencies installed"
    fi
}

# Setup UI environment
setup_ui_environment() {
    if [ "$SKIP_UI" = true ]; then
        log_info "Skipping UI setup as requested"
        return
    fi
    
    log_step "Setting Up UI Environment"
    
    # Check for package.json in various locations
    local ui_paths=("ui/dashboard" "ui/frontend" ".")
    local found_ui=false
    
    for path in "${ui_paths[@]}"; do
        if [ -f "$path/package.json" ]; then
            log_info "Found UI in $path"
            cd "$path"
            
            log_info "Installing Node.js dependencies..."
            npm install --quiet
            log_success "Node.js dependencies installed"
            
            cd - > /dev/null
            found_ui=true
            break
        fi
    done
    
    if [ "$found_ui" = false ]; then
        log_info "No UI package.json found, skipping UI setup"
    fi
}

# Create directories
initialize_directories() {
    log_step "Initializing Project Directories"
    
    local directories=(
        "data"
        "data/auth"
        "logs"
        "config"
        "tests/.pytest_cache"
        "htmlcov"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_success "Created directory: $dir"
        else
            log_info "Directory already exists: $dir"
        fi
    done
}

# Setup environment files
setup_environment_files() {
    log_step "Setting Up Environment Configuration"
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp ".env.example" ".env"
            log_success "Created .env from .env.example"
            log_warning "Please edit .env file with your configuration"
        else
            # Create a basic .env file
            cat > .env << 'EOF'
# AstraGuard AI Configuration
# Generated by setup script

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Database
DATABASE_URL=sqlite:///data/astraguard.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/astraguard.log

# Security
SECRET_KEY=change-this-secret-key-in-production
JWT_SECRET=change-this-jwt-secret-in-production

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Feature Flags
ENABLE_TELEMETRY=true
ENABLE_ANOMALY_DETECTION=true
ENABLE_AUTO_RESPONSE=false

EOF
            log_success "Created default .env file"
            log_warning "Please edit .env file with your configuration"
        fi
    else
        log_info ".env file already exists"
    fi
    
    # Create config files if needed
    if [ ! -f "config/api_keys.json" ]; then
        cat > config/api_keys.json << EOF
{
  "demo_key": {
    "name": "Demo API Key",
    "permissions": ["read", "write"],
    "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "is_active": true
  }
}
EOF
        log_success "Created default API keys configuration"
    fi
}

# Initialize database
initialize_database() {
    log_step "Initializing Database"
    
    log_info "Running database initialization..."
    
    # Try to run initialization script if it exists
    if [ -f "scripts/init_db.py" ]; then
        $PYTHON_CMD scripts/init_db.py
        log_success "Database initialized"
    else
        log_info "No database initialization script found, skipping"
    fi
}

# Run tests
run_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        log_info "Skipping tests as requested"
        return
    fi
    
    log_step "Running Initial Tests"
    
    log_info "Running smoke tests..."
    
    if $PYTHON_CMD -m pytest tests/ -v --tb=short -k "not slow" -x --maxfail=3 &> /dev/null; then
        log_success "Tests passed!"
    else
        log_warning "Some tests failed. This is okay for initial setup."
        log_info "Run 'pytest tests/ -v' to see detailed test results"
    fi
}

# Display summary
show_summary() {
    echo -e "${GREEN}"
    cat << 'EOF'

╔═══════════════════════════════════════════════════════╗
║                                                       ║
║              ✅ Setup Complete!                       ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝

📝 Next Steps:

1. Activate virtual environment (if not already active):
   source venv/bin/activate

2. Edit configuration:
   nano .env  # or your preferred editor

3. Start the API server:
   python -m uvicorn src.api.service:app --reload

4. Start the dashboard (in another terminal):
   cd ui/dashboard
   npm run dev

5. Run tests:
   pytest tests/ -v

6. View API documentation:
   http://localhost:8000/docs

📚 Useful Commands:

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest --cov=src tests/

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
ruff check src/ tests/

🔗 Resources:

- Documentation: docs/
- Technical Guide: docs/TECHNICAL.md
- Contributing: docs/CONTRIBUTING.md
- API Reference: http://localhost:8000/docs (after starting server)

⚠️  Important:

- Remember to activate the virtual environment before working
- Edit .env file with your configuration
- Never commit secrets or API keys
- Check logs/ directory for application logs

🎉 Happy coding with AstraGuard AI!

EOF
    echo -e "${NC}"
}

# Main execution
main() {
    show_banner
    
    log_info "Starting AstraGuard AI local development environment setup..."
    log_info "This will install dependencies and configure your development environment."
    echo ""
    
    check_prerequisites
    setup_python_environment
    setup_ui_environment
    initialize_directories
    setup_environment_files
    initialize_database
    run_tests
    
    show_summary
}

# Run main function
main
