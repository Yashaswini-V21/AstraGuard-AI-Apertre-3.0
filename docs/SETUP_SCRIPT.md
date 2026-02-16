# Local Development Setup Script

Automated setup scripts for configuring the AstraGuard AI local development environment.

## Overview

The setup scripts automate the process of setting up a complete local development environment for AstraGuard AI, including:

- ✅ Prerequisite verification (Python, Node.js, Git)
- ✅ Virtual environment creation and activation
- ✅ Dependency installation (Python packages and Node.js modules)
- ✅ Directory structure initialization
- ✅ Configuration file generation (.env, API keys)
- ✅ Database initialization
- ✅ Optional initial test execution

## Available Scripts

### Windows (PowerShell)

**File**: `setup-dev.ps1`

```powershell
# Basic usage
.\setup-dev.ps1

# Skip tests after setup
.\setup-dev.ps1 -SkipTests

# Skip UI/frontend setup
.\setup-dev.ps1 -SkipUI

# Force reinstallation
.\setup-dev.ps1 -Force

# Combine options
.\setup-dev.ps1 -SkipTests -SkipUI
```

### Linux/macOS (Bash)

**File**: `setup-dev.sh`

```bash
# Make script executable (first time only)
chmod +x setup-dev.sh

# Basic usage
./setup-dev.sh

# Skip tests after setup
./setup-dev.sh --skip-tests

# Skip UI/frontend setup
./setup-dev.sh --skip-ui

# Force reinstallation
./setup-dev.sh --force

# Combine options
./setup-dev.sh --skip-tests --skip-ui

# Show help
./setup-dev.sh --help
```

## Prerequisites

### Minimum Requirements

| Tool | Minimum Version | Purpose |
|------|----------------|---------|
| **Python** | 3.9 | Backend runtime |
| **pip** | Latest | Python package management |
| **Node.js** | 16.0 | Frontend runtime (optional) |
| **npm** | Latest | Node.js package management (optional) |
| **Git** | 2.30 | Version control (recommended) |

### Optional Requirements

| Tool | Purpose |
|------|---------|
| **Docker** | Containerized deployment |
| **Redis** | Caching and message queue |
| **PostgreSQL** | Production database |

## What Gets Installed

### Python Dependencies

From `Requirements.txt`:
- FastAPI - Web framework
- Uvicorn - ASGI server
- SQLAlchemy - Database ORM
- Pydantic - Data validation
- pytest - Testing framework
- And many more...

### Node.js Dependencies

From `package.json` (if UI setup is enabled):
- React/Vue/Angular (depending on UI framework)
- Development tools
- Build dependencies

## Directory Structure Created

```
AstraGuard-AI-Apertre-3.0/
├── venv/                    # Python virtual environment
├── data/                    # Application data
│   └── auth/               # Authentication data
├── logs/                    # Application logs
├── config/                  # Configuration files
│   └── api_keys.json       # API key storage
├── htmlcov/                # Coverage reports
└── .env                    # Environment variables
```

## Configuration Files

### .env File

The setup script creates a `.env` file with default values:

```bash
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
```

⚠️ **Important**: Edit this file with your actual configuration before running the application.

### config/api_keys.json

Default API key configuration:

```json
{
  "demo_key": {
    "name": "Demo API Key",
    "permissions": ["read", "write"],
    "created_at": "2024-01-15T10:30:00Z",
    "is_active": true
  }
}
```

## Post-Setup Steps

After running the setup script:

### 1. Activate Virtual Environment

**Windows (PowerShell)**:
```powershell
.\venv\Scripts\Activate.ps1
```

**Linux/macOS**:
```bash
source venv/bin/activate
```

### 2. Configure Environment

Edit the `.env` file:
```bash
# Windows
notepad .env

# Linux/macOS
nano .env
```

### 3. Start the API Server

```bash
python -m uvicorn src.api.service:app --reload
```

API will be available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 4. Start the Dashboard (if UI is set up)

In a new terminal:

```bash
cd ui/dashboard
npm run dev
```

Dashboard will typically be available at http://localhost:3000

### 5. Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest --cov=src tests/

# Specific test file
pytest tests/test_api.py -v

# Watch mode (requires pytest-watch)
ptw tests/
```

## Command Options

### PowerShell Script Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `-SkipTests` | Switch | False | Skip running tests after setup |
| `-SkipUI` | Switch | False | Skip UI/frontend setup |
| `-Force` | Switch | False | Force reinstallation of environments |

### Bash Script Options

| Option | Description |
|--------|-------------|
| `--skip-tests` | Skip running tests after setup |
| `--skip-ui` | Skip UI/frontend setup |
| `--force` | Force reinstallation of environments |
| `--help` | Show help message |

## Troubleshooting

### Common Issues

#### 1. Python Not Found

**Error**: `Python not found` or `python3: command not found`

**Solution**:
```bash
# Install Python 3.9+
# Windows: Download from python.org
# Ubuntu/Debian:
sudo apt install python3.9 python3-pip

# macOS:
brew install python@3.9
```

#### 2. Permission Denied (Linux/macOS)

**Error**: `Permission denied` when running setup-dev.sh

**Solution**:
```bash
chmod +x setup-dev.sh
./setup-dev.sh
```

#### 3. Execution Policy Error (Windows)

**Error**: `cannot be loaded because running scripts is disabled`

**Solution**:
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then run setup script
.\setup-dev.ps1
```

#### 4. Virtual Environment Already Exists

**Error**: Virtual environment directory already exists

**Solution**:
```bash
# Use --force flag to recreate
./setup-dev.sh --force
```

Or manually remove and rerun:
```bash
# Windows
Remove-Item -Recurse -Force venv
.\setup-dev.ps1

# Linux/macOS
rm -rf venv
./setup-dev.sh
```

#### 5. Node.js Not Found

**Error**: `Node.js not found` during UI setup

**Solution**:
- Install Node.js 16+ from nodejs.org
- Or use nvm (Node Version Manager):
  ```bash
  # Install Node 18
  nvm install 18
  nvm use 18
  ```
- Or skip UI setup:
  ```bash
  ./setup-dev.sh --skip-ui
  ```

#### 6. Port Already in Use

**Error**: Port 8000 already in use when starting server

**Solution**:
```bash
# Change port in .env
API_PORT=8080

# Or specify port directly
uvicorn src.api.service:app --port 8080 --reload
```

#### 7. Database Connection Error

**Error**: Cannot connect to database

**Solution**:
1. Check `DATABASE_URL` in `.env`
2. Ensure `data/` directory exists and is writable
3. Run database initialization:
   ```bash
   python scripts/init_db.py
   ```

#### 8. Module Import Errors

**Error**: `ModuleNotFoundError: No module named 'xyz'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows

# Reinstall dependencies
pip install -r Requirements.txt
```

### Verbose Output

For debugging, run scripts with verbose output:

**PowerShell**:
```powershell
$VerbosePreference = "Continue"
.\setup-dev.ps1
```

**Bash**:
```bash
bash -x ./setup-dev.sh
```

## Manual Setup

If automated setup fails, you can set up manually:

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Environment

```bash
# Windows
.\venv\Scripts\Activate.ps1

# Linux/macOS
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r Requirements.txt
```

### 4. Create Directories

```bash
mkdir -p data/auth logs config htmlcov
```

### 5. Create Configuration

Copy `.env.example` to `.env` (or create manually):
```bash
cp .env.example .env
```

### 6. Initialize Database

```bash
python scripts/init_db.py
```

### 7. Run Tests

```bash
pytest tests/ -v
```

## Continuous Integration

The setup scripts can be used in CI/CD pipelines:

### GitHub Actions Example

```yaml
name: Setup Dev Environment

on: [push, pull_request]

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Run setup script
        run: |
          chmod +x setup-dev.sh
          ./setup-dev.sh --skip-ui
      
      - name: Run tests
        run: |
          source venv/bin/activate
          pytest tests/ -v
```

## Useful Commands

### Development Workflow

```bash
# Activate environment
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows

# Start API server
uvicorn src.api.service:app --reload

# Start UI (separate terminal)
cd ui/dashboard && npm run dev

# Run tests
pytest tests/ -v

# Run with coverage
pytest --cov=src --cov-report=html tests/

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
ruff check src/ tests/
```

### Maintenance

```bash
# Update dependencies
pip install --upgrade -r Requirements.txt

# Freeze dependencies
pip freeze > requirements-frozen.txt

# Clean cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Reset database
rm data/astraguard.db
python scripts/init_db.py
```

## Security Considerations

⚠️ **Important Security Notes**:

1. **Never commit secrets**: The `.env` file is in `.gitignore` - keep it that way
2. **Change default keys**: Update `SECRET_KEY` and `JWT_SECRET` before production
3. **API key management**: Rotate API keys regularly
4. **File permissions**: Ensure sensitive files have appropriate permissions (600)
5. **Virtual environment**: Always activate venv before running code

## Performance Tips

- **Python dependencies**: Use `--no-cache-dir` flag with pip in CI/CD to save space
- **Node modules**: Consider using `npm ci` instead of `npm install` for faster CI builds
- **Database**: Use PostgreSQL in production instead of SQLite
- **Caching**: Enable Redis for better performance
- **Parallel tests**: Use `pytest -n auto` with pytest-xdist for faster test execution

## Related Documentation

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [TECHNICAL.md](TECHNICAL.md) - Technical architecture
- [API Documentation](api/) - API reference
- [README.md](../README.md) - Project overview

## Support

For issues or questions:

1. Check this documentation
2. Review [troubleshooting](#troubleshooting) section
3. Check existing [GitHub Issues](https://github.com/yashaswini-v21/AstraGuard-AI-Apertre-3.0/issues)
4. Create a new issue with:
   - Operating system and version
   - Python version (`python --version`)
   - Error message and stack trace
   - Steps to reproduce

## License

This setup script is part of the AstraGuard AI project and is licensed under the same terms. See [LICENSE](../LICENSE) for details.
