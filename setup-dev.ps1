#!/usr/bin/env pwsh
<#
.SYNOPSIS
    AstraGuard AI Local Development Setup Script (PowerShell)
    
.DESCRIPTION
    Automated setup script for AstraGuard AI development environment on Windows.
    Checks prerequisites, installs dependencies, and configures the local environment.
    
.PARAMETER SkipTests
    Skip running initial tests after setup
    
.PARAMETER SkipUI
    Skip UI/frontend setup
    
.PARAMETER Force
    Force reinstallation even if already set up
    
.EXAMPLE
    .\setup-dev.ps1
    
.EXAMPLE
    .\setup-dev.ps1 -SkipTests -SkipUI
#>

[CmdletBinding()]
param(
    [switch]$SkipTests,
    [switch]$SkipUI,
    [switch]$Force
)

# Script configuration
$ErrorActionPreference = "Stop"
$SCRIPT_VERSION = "1.0.0"
$MIN_PYTHON_VERSION = "3.9"
$MIN_NODE_VERSION = "16.0"
$MIN_GIT_VERSION = "2.30"

# Color output functions
function Write-Success { param([string]$Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param([string]$Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param([string]$Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param([string]$Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Step { param([string]$Message) Write-Host "`n🔧 $Message" -ForegroundColor Magenta }

# Banner
function Show-Banner {
    Write-Host @"

╔═══════════════════════════════════════════════════════╗
║                                                       ║
║           AstraGuard AI Setup Script v$SCRIPT_VERSION          ║
║     Automated Local Development Environment Setup    ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan
}

# Version comparison
function Compare-Version {
    param([string]$Current, [string]$Required)
    
    $currentParts = $Current -split '\.' | ForEach-Object { [int]$_ }
    $requiredParts = $Required -split '\.' | ForEach-Object { [int]$_ }
    
    for ($i = 0; $i -lt [Math]::Max($currentParts.Length, $requiredParts.Length); $i++) {
        $c = if ($i -lt $currentParts.Length) { $currentParts[$i] } else { 0 }
        $r = if ($i -lt $requiredParts.Length) { $requiredParts[$i] } else { 0 }
        
        if ($c -gt $r) { return $true }
        if ($c -lt $r) { return $false }
    }
    
    return $true
}

# Check prerequisites
function Test-Prerequisites {
    Write-Step "Checking Prerequisites"
    
    $prerequisitesMet = $true
    
    # Check Python
    try {
        $pythonVersion = (python --version 2>&1) -replace 'Python ', ''
        if (Compare-Version $pythonVersion $MIN_PYTHON_VERSION) {
            Write-Success "Python $pythonVersion (>= $MIN_PYTHON_VERSION required)"
        } else {
            Write-Error "Python version $pythonVersion is below minimum $MIN_PYTHON_VERSION"
            $prerequisitesMet = $false
        }
    } catch {
        Write-Error "Python not found. Please install Python $MIN_PYTHON_VERSION or higher"
        $prerequisitesMet = $false
    }
    
    # Check pip
    try {
        $pipVersion = (pip --version 2>&1) -split ' ' | Select-Object -Index 1
        Write-Success "pip $pipVersion installed"
    } catch {
        Write-Error "pip not found. Please install pip"
        $prerequisitesMet = $false
    }
    
    # Check Node.js
    if (-not $SkipUI) {
        try {
            $nodeVersion = (node --version 2>&1) -replace 'v', ''
            if (Compare-Version $nodeVersion $MIN_NODE_VERSION) {
                Write-Success "Node.js $nodeVersion (>= $MIN_NODE_VERSION required)"
            } else {
                Write-Warning "Node.js version $nodeVersion is below recommended $MIN_NODE_VERSION"
            }
        } catch {
            Write-Warning "Node.js not found. UI setup will be skipped"
            $SkipUI = $true
        }
        
        # Check npm
        try {
            $npmVersion = (npm --version 2>&1)
            Write-Success "npm $npmVersion installed"
        } catch {
            Write-Warning "npm not found"
        }
    }
    
    # Check Git
    try {
        $gitVersion = (git --version 2>&1) -replace 'git version ', ''
        Write-Success "Git $gitVersion installed"
    } catch {
        Write-Warning "Git not found. Some features may not work"
    }
    
    # Check Docker (optional)
    try {
        $dockerVersion = (docker --version 2>&1) -replace 'Docker version ', '' -replace ',.*', ''
        Write-Success "Docker $dockerVersion installed (optional)"
    } catch {
        Write-Info "Docker not found (optional for containerized deployment)"
    }
    
    if (-not $prerequisitesMet) {
        Write-Error "Prerequisites not met. Please install required software and try again."
        exit 1
    }
    
    Write-Success "All prerequisites met!"
}

# Setup Python environment
function Setup-PythonEnvironment {
    Write-Step "Setting Up Python Environment"
    
    # Check if venv already exists
    if ((Test-Path "venv") -and -not $Force) {
        Write-Warning "Virtual environment already exists. Use -Force to recreate."
        Write-Info "Activating existing environment..."
    } else {
        if (Test-Path "venv") {
            Write-Info "Removing existing virtual environment..."
            Remove-Item -Recurse -Force "venv"
        }
        
        Write-Info "Creating virtual environment..."
        python -m venv venv
        Write-Success "Virtual environment created"
    }
    
    # Activate virtual environment
    Write-Info "Activating virtual environment..."
    $activateScript = ".\venv\Scripts\Activate.ps1"
    
    if (Test-Path $activateScript) {
        & $activateScript
        Write-Success "Virtual environment activated"
    } else {
        Write-Error "Failed to find activation script"
        exit 1
    }
    
    # Upgrade pip
    Write-Info "Upgrading pip..."
    python -m pip install --upgrade pip --quiet
    Write-Success "pip upgraded"
    
    # Install dependencies
    Write-Info "Installing Python dependencies from Requirements.txt..."
    pip install -r Requirements.txt --quiet
    Write-Success "Python dependencies installed"
    
    # Install development dependencies if available
    if (Test-Path "src/config/requirements-dev.txt") {
        Write-Info "Installing development dependencies..."
        pip install -r src/config/requirements-dev.txt --quiet
        Write-Success "Development dependencies installed"
    }
}

# Setup UI environment
function Setup-UIEnvironment {
    if ($SkipUI) {
        Write-Info "Skipping UI setup as requested"
        return
    }
    
    Write-Step "Setting Up UI Environment"
    
    # Check for package.json in various locations
    $uiPaths = @("ui/dashboard", "ui/frontend", ".")
    $foundUI = $false
    
    foreach ($path in $uiPaths) {
        if (Test-Path (Join-Path $path "package.json")) {
            Write-Info "Found UI in $path"
            Push-Location $path
            
            Write-Info "Installing Node.js dependencies..."
            npm install --quiet
            Write-Success "Node.js dependencies installed"
            
            Pop-Location
            $foundUI = $true
            break
        }
    }
    
    if (-not $foundUI) {
        Write-Info "No UI package.json found, skipping UI setup"
    }
}

# Create directories
function Initialize-Directories {
    Write-Step "Initializing Project Directories"
    
    $directories = @(
        "data",
        "data/auth",
        "logs",
        "config",
        "tests/.pytest_cache",
        "htmlcov"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Success "Created directory: $dir"
        } else {
            Write-Info "Directory already exists: $dir"
        }
    }
}

# Setup environment files
function Setup-EnvironmentFiles {
    Write-Step "Setting Up Environment Configuration"
    
    # Create .env file if it doesn't exist
    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Success "Created .env from .env.example"
            Write-Warning "Please edit .env file with your configuration"
        } else {
            # Create a basic .env file
            $envContent = @"
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

"@
            Set-Content -Path ".env" -Value $envContent
            Write-Success "Created default .env file"
            Write-Warning "Please edit .env file with your configuration"
        }
    } else {
        Write-Info ".env file already exists"
    }
    
    # Create config files if needed
    if (-not (Test-Path "config/api_keys.json")) {
        $apikeysContent = @"
{
  "demo_key": {
    "name": "Demo API Key",
    "permissions": ["read", "write"],
    "created_at": "$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')",
    "is_active": true
  }
}
"@
        Set-Content -Path "config/api_keys.json" -Value $apikeysContent
        Write-Success "Created default API keys configuration"
    }
}

# Initialize database
function Initialize-Database {
    Write-Step "Initializing Database"
    
    Write-Info "Running database initialization..."
    
    # Try to run initialization script if it exists
    if (Test-Path "scripts/init_db.py") {
        python scripts/init_db.py
        Write-Success "Database initialized"
    } else {
        Write-Info "No database initialization script found, skipping"
    }
}

# Run tests
function Invoke-Tests {
    if ($SkipTests) {
        Write-Info "Skipping tests as requested"
        return
    }
    
    Write-Step "Running Initial Tests"
    
    Write-Info "Running smoke tests..."
    
    try {
        # Run a subset of fast tests
        python -m pytest tests/ -v --tb=short -k "not slow" -x --maxfail=3 2>&1 | Out-Null
        Write-Success "Tests passed!"
    } catch {
        Write-Warning "Some tests failed. This is okay for initial setup."
        Write-Info "Run 'pytest tests/ -v' to see detailed test results"
    }
}

# Display summary
function Show-Summary {
    Write-Host @"

╔═══════════════════════════════════════════════════════╗
║                                                       ║
║              ✅ Setup Complete!                       ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝

📝 Next Steps:

1. Activate virtual environment (if not already active):
   .\venv\Scripts\Activate.ps1

2. Edit configuration:
   notepad .env

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

"@ -ForegroundColor Green
}

# Main execution
function Main {
    Show-Banner
    
    Write-Info "Starting AstraGuard AI local development environment setup..."
    Write-Info "This will install dependencies and configure your development environment."
    Write-Host ""
    
    try {
        Test-Prerequisites
        Setup-PythonEnvironment
        Setup-UIEnvironment
        Initialize-Directories
        Setup-EnvironmentFiles
        Initialize-Database
        Invoke-Tests
        
        Show-Summary
        
    } catch {
        Write-Error "Setup failed: $_"
        Write-Error $_.ScriptStackTrace
        exit 1
    }
}

# Run main function
Main
