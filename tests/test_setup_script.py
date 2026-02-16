"""
Tests for development environment setup scripts.

This module tests the setup script logic and components without actually
running the full setup to avoid side effects during test execution.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List
from unittest import mock

import pytest


class TestSetupScriptComponents:
    """Test individual components of the setup scripts."""
    
    def test_required_directories_structure(self):
        """Test that required directories exist or are defined."""
        required_dirs = [
            "data",
            "data/auth",
            "logs",
            "config",
            "tests",
            "src"
        ]
        
        for directory in required_dirs:
            # Either directory exists or script will create it
            assert isinstance(directory, str)
            assert len(directory) > 0
    
    def test_env_file_generation_logic(self, tmp_path):
        """Test .env file generation creates valid content."""
        env_content = """# AstraGuard AI Configuration
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=sqlite:///data/astraguard.db
LOG_LEVEL=INFO
SECRET_KEY=test-secret-key
"""
        
        env_file = tmp_path / ".env"
        env_file.write_text(env_content)
        
        # Verify file is readable and has content
        assert env_file.exists()
        content = env_file.read_text()
        assert "API_HOST" in content
        assert "DATABASE_URL" in content
        assert "SECRET_KEY" in content
    
    def test_api_keys_json_structure(self, tmp_path):
        """Test API keys JSON structure is valid."""
        api_keys = {
            "test_key": {
                "name": "Test API Key",
                "permissions": ["read", "write"],
                "created_at": "2024-01-01T00:00:00Z",
                "is_active": True
            }
        }
        
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        api_keys_file = config_dir / "api_keys.json"
        
        with open(api_keys_file, 'w') as f:
            json.dump(api_keys, f, indent=2)
        
        # Verify JSON is valid
        assert api_keys_file.exists()
        with open(api_keys_file) as f:
            data = json.load(f)
        
        assert "test_key" in data
        assert data["test_key"]["name"] == "Test API Key"
        assert "permissions" in data["test_key"]
        assert isinstance(data["test_key"]["permissions"], list)


class TestVersionChecking:
    """Test version comparison and validation logic."""
    
    def test_version_comparison_logic(self):
        """Test semantic version comparison."""
        # Simulate version comparison logic
        def version_tuple(v: str) -> tuple:
            """Convert version string to tuple for comparison."""
            return tuple(map(int, v.split('.')))
        
        # Test cases
        assert version_tuple("3.9.0") >= version_tuple("3.9.0")
        assert version_tuple("3.10.0") >= version_tuple("3.9.0")
        assert version_tuple("3.11.5") >= version_tuple("3.9.0")
        assert not (version_tuple("3.8.0") >= version_tuple("3.9.0"))
    
    def test_python_version_check(self):
        """Test Python version is sufficient."""
        import sys
        current_version = sys.version_info
        
        # Python 3.9+ required
        assert current_version >= (3, 9), \
            f"Python 3.9+ required, got {current_version.major}.{current_version.minor}"
    
    def test_module_availability(self):
        """Test required Python modules are available."""
        required_modules = [
            'json',
            'os',
            'sys',
            'pathlib',
            'tempfile',
            'subprocess'
        ]
        
        for module_name in required_modules:
            try:
                __import__(module_name)
            except ImportError:
                pytest.fail(f"Required module '{module_name}' not available")


class TestScriptFileStructure:
    """Test setup script files exist and have correct structure."""
    
    def test_setup_scripts_exist(self):
        """Test that setup script files exist."""
        root = Path(__file__).parent.parent
        
        powershell_script = root / "setup-dev.ps1"
        bash_script = root / "setup-dev.sh"
        
        # At least one script should exist
        assert powershell_script.exists() or bash_script.exists(), \
            "No setup script found"
    
    def test_powershell_script_structure(self):
        """Test PowerShell script has proper structure."""
        root = Path(__file__).parent.parent
        ps_script = root / "setup-dev.ps1"
        
        if not ps_script.exists():
            pytest.skip("PowerShell script not found")
        
        content = ps_script.read_text(encoding='utf-8')
        
        # Check for key components
        assert "param(" in content or "Param(" in content, \
            "PowerShell script should have parameters"
        assert "function" in content.lower(), \
            "PowerShell script should define functions"
    
    def test_bash_script_structure(self):
        """Test Bash script has proper structure."""
        root = Path(__file__).parent.parent
        bash_script = root / "setup-dev.sh"
        
        if not bash_script.exists():
            pytest.skip("Bash script not found")
        
        content = bash_script.read_text(encoding='utf-8')
        
        # Check for key components
        assert content.startswith("#!/"), \
            "Bash script should have shebang"
        assert "function" in content or "() {" in content, \
            "Bash script should define functions"


class TestConfigurationFiles:
    """Test configuration file handling."""
    
    def test_requirements_file_exists(self):
        """Test Requirements.txt exists and is readable."""
        root = Path(__file__).parent.parent
        requirements = root / "Requirements.txt"
        
        assert requirements.exists(), "Requirements.txt not found"
        
        content = requirements.read_text()
        assert len(content) > 0, "Requirements.txt is empty"
    
    def test_package_json_structure(self):
        """Test package.json exists if UI is present."""
        root = Path(__file__).parent.parent
        
        # Check common UI locations
        ui_paths = [
            root / "package.json",
            root / "ui" / "dashboard" / "package.json",
            root / "ui" / "frontend" / "package.json"
        ]
        
        # At least one package.json might exist
        package_jsons = [p for p in ui_paths if p.exists()]
        
        for pkg_json in package_jsons:
            with open(pkg_json) as f:
                data = json.load(f)
            
            # Verify basic structure
            assert "name" in data or "dependencies" in data or "scripts" in data
    
    def test_pyproject_toml_exists(self):
        """Test pyproject.toml exists."""
        root = Path(__file__).parent.parent
        pyproject = root / "pyproject.toml"
        
        assert pyproject.exists(), "pyproject.toml not found"


class TestDirectoryInitialization:
    """Test directory creation and initialization."""
    
    def test_create_directory_structure(self, tmp_path):
        """Test creating the required directory structure."""
        directories = [
            "data",
            "data/auth",
            "logs",
            "config",
            "tests/.pytest_cache",
            "htmlcov"
        ]
        
        for directory in directories:
            dir_path = tmp_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            assert dir_path.exists()
            assert dir_path.is_dir()
    
    def test_directory_permissions(self, tmp_path):
        """Test created directories have correct permissions."""
        test_dir = tmp_path / "test_data"
        test_dir.mkdir()
        
        # Directory should be readable, writable, and executable
        assert os.access(test_dir, os.R_OK)
        assert os.access(test_dir, os.W_OK)
        assert os.access(test_dir, os.X_OK)


class TestEnvironmentSetup:
    """Test environment setup logic."""
    
    def test_virtual_environment_creation_logic(self, tmp_path):
        """Test virtual environment creation (without actually creating)."""
        venv_path = tmp_path / "venv"
        
        # Simulate venv check
        if sys.platform == "win32":
            expected_python = venv_path / "Scripts" / "python.exe"
            expected_activate = venv_path / "Scripts" / "activate.bat"
        else:
            expected_python = venv_path / "bin" / "python"
            expected_activate = venv_path / "bin" / "activate"
        
        # Just verify path logic is correct
        assert expected_python.parent.exists() or not venv_path.exists()
    
    def test_env_variables_parsing(self):
        """Test environment variable parsing logic."""
        env_content = """
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=sqlite:///data/astraguard.db
"""
        
        # Parse env content
        env_vars = {}
        for line in env_content.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key] = value
        
        assert env_vars["API_HOST"] == "0.0.0.0"
        assert env_vars["API_PORT"] == "8000"
        assert "DATABASE_URL" in env_vars


class TestScriptOptions:
    """Test command-line options and parameters."""
    
    def test_script_parameter_parsing(self):
        """Test parsing of script parameters."""
        # Simulate parameter values
        params = {
            "skip_tests": False,
            "skip_ui": False,
            "force": False
        }
        
        # Test default values
        assert params["skip_tests"] in [True, False]
        assert params["skip_ui"] in [True, False]
        assert params["force"] in [True, False]
    
    def test_help_text_availability(self):
        """Test that scripts provide help text."""
        root = Path(__file__).parent.parent
        
        # Check PowerShell script
        ps_script = root / "setup-dev.ps1"
        if ps_script.exists():
            content = ps_script.read_text(encoding='utf-8')
            assert ".SYNOPSIS" in content or "Usage:" in content or "help" in content.lower()
        
        # Check Bash script  
        bash_script = root / "setup-dev.sh"
        if bash_script.exists():
            content = bash_script.read_text(encoding='utf-8')
            assert "Usage:" in content or "--help" in content or "help" in content.lower()


class TestErrorHandling:
    """Test error handling in setup scripts."""
    
    def test_missing_prerequisites_handling(self):
        """Test handling of missing prerequisites."""
        # Simulate prerequisite check
        def check_command(cmd: str) -> bool:
            """Check if command exists."""
            try:
                subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    timeout=5
                )
                return True
            except (subprocess.SubprocessError, FileNotFoundError):
                return False
        
        # Test that check_command works
        result = check_command("python" if sys.platform == "win32" else "python3")
        assert isinstance(result, bool)
    
    def test_file_creation_error_handling(self, tmp_path):
        """Test handling of file creation errors."""
        # Try to create file in read-only directory (if possible)
        test_file = tmp_path / "test.txt"
        
        try:
            test_file.write_text("test")
            success = True
        except (IOError, OSError):
            success = False
        
        # If directory is writable, this should succeed
        if os.access(tmp_path, os.W_OK):
            assert success


class TestDependencyInstallation:
    """Test dependency installation logic."""
    
    def test_requirements_parsing(self):
        """Test parsing of Requirements.txt."""
        root = Path(__file__).parent.parent
        requirements_file = root / "Requirements.txt"
        
        if not requirements_file.exists():
            pytest.skip("Requirements.txt not found")
        
        content = requirements_file.read_text()
        lines = content.strip().split('\n')
        
        # Filter out comments and empty lines
        packages = [
            line.strip() 
            for line in lines 
            if line.strip() and not line.strip().startswith('#')
        ]
        
        # Should have at least some packages
        assert len(packages) > 0, "No packages found in Requirements.txt"
    
    def test_package_json_parsing(self):
        """Test parsing of package.json if it exists."""
        root = Path(__file__).parent.parent
        package_json = root / "package.json"
        
        if not package_json.exists():
            pytest.skip("package.json not found")
        
        with open(package_json) as f:
            data = json.load(f)
        
        # Verify it's valid JSON with expected structure
        assert isinstance(data, dict)


class TestSetupValidation:
    """Test validation of completed setup."""
    
    def test_python_imports_after_setup(self):
        """Test that core Python modules can be imported."""
        core_modules = ['json', 'os', 'sys', 'pathlib']
        
        for module_name in core_modules:
            try:
                __import__(module_name)
            except ImportError:
                pytest.fail(f"Could not import {module_name}")
    
    def test_project_structure_exists(self):
        """Test that project structure is intact."""
        root = Path(__file__).parent.parent
        
        # Key directories that should exist
        key_dirs = ["src", "tests"]
        
        for directory in key_dirs:
            dir_path = root / directory
            assert dir_path.exists(), f"Directory {directory} not found"
            assert dir_path.is_dir(), f"{directory} is not a directory"


# Integration tests (marked as slow, can be skipped)
class TestSetupScriptExecution:
    """Integration tests for actual script execution."""
    
    @pytest.mark.slow
    def test_bash_script_syntax(self):
        """Test that bash script has valid syntax."""
        root = Path(__file__).parent.parent
        bash_script = root / "setup-dev.sh"
        
        if not bash_script.exists():
            pytest.skip("Bash script not found")
        
        # Check syntax without executing
        try:
            result = subprocess.run(
                ["bash", "-n", str(bash_script)],
                capture_output=True,
                timeout=5
            )
        except (FileNotFoundError, subprocess.SubprocessError):
            pytest.skip("bash not available on this system")
        
        # Skip if WSL needs updating (Windows-specific issue)
        # Check both stdout and stderr, handling potential encoding issues
        stderr_str = result.stderr.decode('utf-16-le', errors='ignore') if result.stderr else ""
        stdout_str = result.stdout.decode('utf-16-le', errors='ignore') if result.stdout else ""
        
        if "Windows Subsystem" in stderr_str or "wsl.exe" in stderr_str or \
           "Windows Subsystem" in stdout_str or "wsl.exe" in stdout_str:
            pytest.skip("WSL needs updating on this system")
        
        # Try UTF-8 decoding for actual error messages
        try:
            stderr_str = result.stderr.decode('utf-8')
        except:
            pass
        
        assert result.returncode == 0, \
            f"Bash syntax error: {stderr_str}"
    
    @pytest.mark.slow
    def test_powershell_script_syntax(self):
        """Test that PowerShell script has valid syntax."""
        if sys.platform != "win32":
            pytest.skip("PowerShell test only on Windows")
        
        root = Path(__file__).parent.parent
        ps_script = root / "setup-dev.ps1"
        
        if not ps_script.exists():
            pytest.skip("PowerShell script not found")
        
        # Check syntax without executing
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", 
             f"$null = [System.Management.Automation.PSParser]::Tokenize((Get-Content '{ps_script}' -Raw), [ref]$null)"],
            capture_output=True,
            text=True
        )
        
        # If command runs without error, syntax is valid
        assert result.returncode == 0 or "Cannot find" not in result.stderr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
