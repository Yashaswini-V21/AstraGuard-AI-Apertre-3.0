#!/usr/bin/env python3
"""
Development Environment Validator for AstraGuard AI
Validates that the development environment meets all requirements.
"""

import sys
import subprocess
import importlib.util
from pathlib import Path
from typing import List, Tuple

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is >= 3.9"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Python {version.major}.{version.minor}.{version.micro} (requires >= 3.9)"

def check_nodejs() -> Tuple[bool, str]:
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True, f"Node.js {result.stdout.strip()}"
        return False, "Node.js not available"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, "Node.js not found"

def check_package(package_name: str) -> Tuple[bool, str]:
    """Check if a Python package is installed"""
    spec = importlib.util.find_spec(package_name)
    if spec is not None:
        try:
            module = importlib.import_module(package_name)
            version = getattr(module, "__version__", "installed")
            return True, f"{package_name} {version}"
        except ImportError:
            return True, f"{package_name} (version unknown)"
    return False, f"{package_name} not installed"

def check_required_files() -> List[Tuple[str, bool]]:
    """Check if required configuration and setup files exist"""
    project_root = Path(__file__).parent.parent
    required_files = [
        "pyproject.toml",
        "package.json",
        "setup.py",
        "src/config/requirements.txt",
        "README.md"
    ]
    
    results = []
    for file_path in required_files:
        full_path = project_root / file_path
        results.append((file_path, full_path.exists()))
    return results

def check_required_directories() -> List[Tuple[str, bool]]:
    """Check if required directories exist"""
    project_root = Path(__file__).parent.parent
    required_dirs = [
        "src",
        "tests",
        "scripts",
        "config",
        "docs"
    ]
    
    results = []
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        results.append((dir_path, full_path.exists() and full_path.is_dir()))
    return results

def main():
    """Run all validation checks"""
    print("\n" + "="*60)
    print("  AstraGuard AI - Development Environment Validator")
    print("="*60 + "\n")
    
    all_passed = True
    
    # Check Python version
    print("🔍 Checking Python version...")
    success, msg = check_python_version()
    print(f"  {GREEN}✓{RESET} {msg}" if success else f"  {RED}✗{RESET} {msg}")
    all_passed &= success
    
    # Check Node.js
    print("\n🔍 Checking Node.js...")
    success, msg = check_nodejs()
    print(f"  {GREEN}✓{RESET} {msg}" if success else f"  {YELLOW}⚠{RESET} {msg} (optional for backend dev)")
    
    # Check critical Python packages
    print("\n🔍 Checking critical Python packages...")
    critical_packages = ["fastapi", "numpy", "pandas", "torch", "pydantic"]
    for package in critical_packages:
        success, msg = check_package(package)
        print(f"  {GREEN}✓{RESET} {msg}" if success else f"  {RED}✗{RESET} {msg}")
        all_passed &= success
    
    # Check required files
    print("\n🔍 Checking required files...")
    file_results = check_required_files()
    for file_path, exists in file_results:
        if exists:
            print(f"  {GREEN}✓{RESET} {file_path}")
        else:
            print(f"  {RED}✗{RESET} {file_path} (missing)")
            all_passed = False
    
    # Check required directories
    print("\n🔍 Checking required directories...")
    dir_results = check_required_directories()
    for dir_path, exists in dir_results:
        if exists:
            print(f"  {GREEN}✓{RESET} {dir_path}/")
        else:
            print(f"  {RED}✗{RESET} {dir_path}/ (missing)")
            all_passed = False
    
    # Final summary
    print("\n" + "="*60)
    if all_passed:
        print(f"{GREEN}✓ Development environment is ready!{RESET}")
        print("="*60 + "\n")
        return 0
    else:
        print(f"{RED}✗ Development environment has issues{RESET}")
        print("\nTo fix missing packages, run:")
        print("  pip install -r src/config/requirements.txt")
        print("="*60 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
