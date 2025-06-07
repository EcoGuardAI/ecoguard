#!/usr/bin/env python3
"""
Version management script for EcoGuard AI.
This script helps with version bumping and release preparation.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def get_current_version():
    """Get current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")

    content = pyproject_path.read_text()
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        raise ValueError("Version not found in pyproject.toml")

    return match.group(1)


def update_version_in_file(file_path, old_version, new_version):
    """Update version in a specific file."""
    if not file_path.exists():
        print(f"Warning: {file_path} not found, skipping...")
        return

    content = file_path.read_text()

    if file_path.name == "pyproject.toml":
        # Update version in pyproject.toml
        content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)
    elif file_path.name == "__init__.py" and "cli" in str(file_path):
        # Update version in CLI
        content = re.sub(
            r'@click\.version_option\(version="[^"]*"',
            f'@click.version_option(version="{new_version}"',
            content,
        )

    file_path.write_text(content)
    print(f"Updated version in {file_path}")


def validate_version(version):
    """Validate semantic version format."""
    pattern = r"^\d+\.\d+\.\d+(?:-(?:alpha|beta|rc)\.\d+)?$"
    if not re.match(pattern, version):
        raise ValueError(
            f"Invalid version format: {version}. "
            "Expected format: X.Y.Z or X.Y.Z-alpha.N, X.Y.Z-beta.N, X.Y.Z-rc.N"
        )


def bump_version(current_version, bump_type):
    """Bump version based on bump type."""
    parts = current_version.split(".")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def git_check_clean():
    """Check if git working directory is clean."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
        )
        return len(result.stdout.strip()) == 0
    except subprocess.CalledProcessError:
        return False


def run_tests():
    """Run test suite."""
    print("Running test suite...")
    try:
        subprocess.run(["pytest", "tests/", "-v"], check=True)
        print("✅ Tests passed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Tests failed")
        return False


def run_linting():
    """Run linting checks."""
    print("Running linting checks...")
    try:
        subprocess.run(["black", "--check", "src/", "tests/"], check=True)
        subprocess.run(["isort", "--check-only", "src/", "tests/"], check=True)
        subprocess.run(["ruff", "check", "src/", "tests/"], check=True)
        print("✅ Linting passed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Linting failed")
        return False


def main():
    parser = argparse.ArgumentParser(description="EcoGuard AI Version Management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Current version command
    subparsers.add_parser("current", help="Show current version")

    # Bump version command
    bump_parser = subparsers.add_parser("bump", help="Bump version")
    bump_parser.add_argument(
        "type", choices=["major", "minor", "patch"], help="Type of version bump"
    )
    bump_parser.add_argument(
        "--no-test", action="store_true", help="Skip running tests"
    )
    bump_parser.add_argument(
        "--no-lint", action="store_true", help="Skip linting checks"
    )

    # Set version command
    set_parser = subparsers.add_parser("set", help="Set specific version")
    set_parser.add_argument("version", help="Version to set")
    set_parser.add_argument("--no-test", action="store_true", help="Skip running tests")
    set_parser.add_argument(
        "--no-lint", action="store_true", help="Skip linting checks"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        current_version = get_current_version()

        if args.command == "current":
            print(f"Current version: {current_version}")
            return

        # Check git status
        if not git_check_clean():
            print("Warning: Git working directory is not clean")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != "y":
                print("Aborted")
                return

        # Determine new version
        if args.command == "bump":
            new_version = bump_version(current_version, args.type)
        else:  # set
            new_version = args.version
            validate_version(new_version)

        print(f"Updating version: {current_version} → {new_version}")

        # Run tests and linting if requested
        if not args.no_test and not run_tests():
            print("Aborted due to test failures")
            return

        if not args.no_lint and not run_linting():
            print("Aborted due to linting failures")
            return

        # Update version in files
        files_to_update = [
            Path("pyproject.toml"),
            Path("src/ecoguard_ai/cli/__init__.py"),
        ]

        for file_path in files_to_update:
            update_version_in_file(file_path, current_version, new_version)

        print(f"✅ Version updated to {new_version}")
        print("\nNext steps:")
        print("1. Review the changes")
        print("2. Commit the version bump")
        print("3. Create a tag: git tag v" + new_version)
        print("4. Push changes: git push origin main --tags")
        print("5. Or use the GitHub release workflow")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
