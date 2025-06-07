#!/usr/bin/env python3
"""Development environment setup script for EcoGuard AI.

This script sets up the development environment with all necessary dependencies
and tools for EcoGuard AI development.

Usage:
    python scripts/setup_dev.py
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str) -> bool:
    """
    Run a command and return True if successful.

    Args:
        cmd: The shell command to execute
        description: Description of what the command does

    Returns:
        True if command succeeded, False otherwise
    """
    print(f"🔧 {description}...")
    try:
        # Using shell=True with trusted input for development setup
        subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )  # nosec B602
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Command: {cmd}")
        print(f"Error: {e.stderr}")
        return False


def main() -> None:
    """
    Set up the development environment.

    This function installs all necessary dependencies, sets up pre-commit hooks,
    runs initial checks, and provides guidance for next steps.

    Returns:
        None

    Exits:
        System exit with code 1 if Python version is too old
    """
    print("🌱 Setting up EcoGuard AI development environment...\n")

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"📁 Working in: {project_root.absolute()}")

    # Install the package in development mode
    if not run_command(
        "pip install -e .[dev,runtime,security]",
        "Installing EcoGuard AI in development mode",
    ):
        return False

    # Install pre-commit hooks
    if not run_command("pre-commit install", "Installing pre-commit hooks"):
        return False

    # Run initial pre-commit on all files
    if not run_command(
        "pre-commit run --all-files", "Running initial pre-commit checks"
    ):
        print("⚠️  Pre-commit checks failed, but continuing setup...")

    # Initialize secrets baseline if it doesn't exist
    if not Path(".secrets.baseline").exists():
        run_command(
            "detect-secrets scan > .secrets.baseline", "Creating secrets baseline"
        )

    # Run tests to verify setup
    if not run_command("pytest tests/ --maxfail=5", "Running test suite"):
        print("⚠️  Some tests failed, but setup is complete")

    # Run EcoGuard AI self-analysis
    run_command(
        "ecoguard analyze src/ --format table", "Running EcoGuard AI self-analysis"
    )

    print("\n🎉 Development environment setup complete!")
    print("\n📋 Next steps:")
    print("  1. Start developing with: code .")
    print("  2. Run tests with: pytest")
    print("  3. Run linting with: tox -e lint")
    print("  4. Run all checks with: tox")
    print("  5. Analyze code with: ecoguard analyze <path>")
    print("\n📚 Useful commands:")
    print("  - Format code: tox -e format")
    print("  - Type check: tox -e type")
    print("  - Security scan: tox -e security")
    print("  - Clean environment: tox -e clean")

    return True


if __name__ == "__main__":
    success = main()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
