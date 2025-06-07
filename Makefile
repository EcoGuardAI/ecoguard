# Makefile for EcoGuard AI Development
#
# This Makefile provides convenient commands for common development tasks.
# It works on Linux, macOS, and Windows (with make installed).

.PHONY: help install dev-install test lint format type-check security clean docs build all ci self-analyze

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "EcoGuard AI Development Commands"
	@echo "================================"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the package in development mode
	pip install -e .

dev-install: ## Install all development dependencies
	pip install -e .[dev,runtime,security,ai]
	pre-commit install

test: ## Run the test suite
	pytest tests/ -v --cov=src/ecoguard_ai --cov-report=term-missing

test-all: ## Run tests with tox across all Python versions
	tox

lint: ## Run all linting checks
	black --check --diff src/ tests/
	isort --check-only --diff src/ tests/
	flake8 src/ tests/
	ruff check src/ tests/

format: ## Format code with black and isort
	black src/ tests/
	isort src/ tests/

type-check: ## Run type checking with mypy
	mypy src/ --strict

security: ## Run security checks
	bandit -r src/
	safety check
	pip-audit

docs: ## Build documentation (placeholder)
	@echo "📚 Documentation build will be implemented in future stages"

build: ## Build the package
	python -m build

clean: ## Clean up build artifacts and caches
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .tox/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -f .coverage
	rm -f coverage.xml
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

self-analyze: ## Run EcoGuard AI analysis on itself
	ecoguard analyze src/ --format table
	@echo ""
	@echo "📊 Running comprehensive analysis..."
	ecoguard analyze . --format json --output self-analysis-results.json

pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

setup-dev: ## Set up development environment from scratch
	python scripts/setup_dev.py

ci: lint type-check test security ## Run all CI checks locally
	@echo "✅ All CI checks passed!"

all: clean dev-install pre-commit test ci self-analyze ## Run complete development setup and checks
	@echo "🎉 All development tasks completed successfully!"

# Docker commands (for future use)
docker-build: ## Build Docker image (placeholder)
	@echo "🐳 Docker build will be implemented in future stages"

docker-test: ## Run tests in Docker (placeholder)
	@echo "🐳 Docker test will be implemented in future stages"

# Performance testing
perf-test: ## Run performance benchmarks
	pytest tests/ -k "benchmark" --benchmark-only

# Dependency management
update-deps: ## Update all dependencies
	pip list --outdated --format=json | python -c "import json, sys; packages = [p['name'] for p in json.load(sys.stdin)]; print('\n'.join(packages))" | xargs -r pip install -U

check-deps: ## Check for dependency vulnerabilities
	pip-audit
	safety check

# Release commands (for future use)
version: ## Show current version
	python -c "import toml; print(toml.load('pyproject.toml')['project']['version'])"

release-check: ## Check if ready for release
	@echo "🔍 Checking release readiness..."
	check-manifest
	python -m build
	twine check dist/*
	@echo "✅ Release checks passed!"
