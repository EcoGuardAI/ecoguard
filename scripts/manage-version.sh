#!/bin/bash
# EcoGuard AI Version Management Helper Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# Make sure Python script is executable
chmod +x scripts/version.py

# Function to show help
show_help() {
    echo "EcoGuard AI Version Management Helper"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  current              Show current version"
    echo "  bump major          Bump major version (X.0.0)"
    echo "  bump minor          Bump minor version (X.Y.0)"
    echo "  bump patch          Bump patch version (X.Y.Z)"
    echo "  set <version>       Set specific version"
    echo "  release <version>   Create a release (bump version + create tag)"
    echo "  status              Show project status"
    echo "  help                Show this help message"
    echo ""
    echo "Options:"
    echo "  --no-test           Skip running tests"
    echo "  --no-lint           Skip linting checks"
    echo ""
    echo "Examples:"
    echo "  $0 current"
    echo "  $0 bump patch"
    echo "  $0 set 0.2.0"
    echo "  $0 release 0.2.0"
}

# Function to show project status
show_status() {
    print_status "EcoGuard AI Project Status"
    echo ""

    # Current version
    current_version=$(python3 scripts/version.py current | cut -d' ' -f3)
    echo "Current version: $current_version"

    # Git status
    if git status --porcelain | grep -q .; then
        print_warning "Git working directory has uncommitted changes"
        git status --porcelain
    else
        print_success "Git working directory is clean"
    fi

    # Last commit
    echo "Last commit: $(git log -1 --oneline)"

    # Tags
    echo "Recent tags:"
    git tag -l | tail -5 | sed 's/^/  /'

    # Check if tests pass
    echo ""
    print_status "Running quick health check..."
    if python3 -m pytest tests/ -x -q > /dev/null 2>&1; then
        print_success "Tests are passing"
    else
        print_warning "Some tests are failing"
    fi
}

# Function to create a release
create_release() {
    local version=$1
    local no_test=$2
    local no_lint=$3

    print_status "Creating release for version $version"

    # Update version
    python3 scripts/version.py set "$version" $no_test $no_lint

    if [ $? -eq 0 ]; then
        print_success "Version updated successfully"

        # Create git commit and tag
        print_status "Creating git commit and tag..."
        git add pyproject.toml src/ecoguard_ai/cli/__init__.py
        git commit -m "chore: bump version to $version"
        git tag "v$version"

        print_success "Release v$version created successfully!"
        echo ""
        echo "To publish the release:"
        echo "  git push origin main"
        echo "  git push origin v$version"
        echo ""
        echo "Or use the GitHub release workflow for a more controlled release."
    else
        print_error "Failed to update version"
        exit 1
    fi
}

# Parse arguments
case "${1:-}" in
    "current")
        python3 scripts/version.py current
        ;;
    "bump")
        if [ -z "${2:-}" ]; then
            print_error "Bump type required (major, minor, patch)"
            exit 1
        fi
        python3 scripts/version.py bump "$2" "${@:3}"
        ;;
    "set")
        if [ -z "${2:-}" ]; then
            print_error "Version required"
            exit 1
        fi
        python3 scripts/version.py set "$2" "${@:3}"
        ;;
    "release")
        if [ -z "${2:-}" ]; then
            print_error "Version required"
            exit 1
        fi
        create_release "$2" "${@:3}"
        ;;
    "status")
        show_status
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
