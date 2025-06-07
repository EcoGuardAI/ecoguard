# Pre-Push Commands for EcoGuard AI

This document contains all the essential commands to run before pushing code to ensure code quality, functionality, and consistency.

## 🚀 Quick Start (Recommended Workflow)

```bash
# Complete pre-push workflow in one command
make lint && make test && make build
```

## 📋 Detailed Pre-Push Checklist

### 1. Environment Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Update pre-commit hooks (if using)
pre-commit install
pre-commit autoupdate
```

### 2. Code Formatting & Style

```bash
# Format code with Black
black src/ tests/ examples/

# Sort imports with isort
isort src/ tests/ examples/

# Check formatting (without making changes)
black --check src/ tests/ examples/
isort --check-only src/ tests/ examples/
```

### 3. Linting & Code Quality

```bash
# Run flake8 linting
flake8 src/ tests/ examples/

# Run ruff linting (modern, fast linter)
ruff check src/ tests/ examples/

# Check docstring style
pydocstyle src/

# Check code complexity
flake8 --select=C901 src/
```

### 4. Type Checking

```bash
# Run mypy type checking
mypy src/

# Type check with strict mode (optional)
mypy --strict src/ecoguard_ai/
```

### 5. Security Checks

```bash
# Check for security vulnerabilities
bandit -r src/

# Check for secrets in code
detect-secrets scan --all-files

# Check dependency vulnerabilities
safety check

# Check for known security issues
pip-audit
```

### 6. Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/ecoguard_ai --cov-report=html --cov-report=term

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest -m "not slow"  # Skip slow tests
```

### 7. Package Verification

```bash
# Check package manifest
check-manifest

# Test package building
python -m build

# Verify package installation
pip install dist/*.whl --force-reinstall
```

### 8. CLI Functionality Tests

```bash
# Test CLI entry points
python -m ecoguard_ai --version
ecoguard --version

# Test core analysis functionality
ecoguard analyze examples/basic_usage.py --format table
ecoguard analyze examples/basic_usage.py --format json --output test-results.json

# Test CLI help and rules
ecoguard --help
ecoguard rules --list
```

### 9. Self-Analysis (EcoGuard AI analyzing itself)

```bash
# Analyze the project with EcoGuard AI
ecoguard analyze src/ --format table
ecoguard analyze src/ --format json --output self-analysis.json

# Check analysis results
cat self-analysis.json | jq '.summary'
```

### 10. Documentation Checks

```bash
# Check README links and formatting
markdown-link-check README.md

# Validate documentation structure
sphinx-build -b html docs/ docs/_build/html -W
```

## 🔄 Automated Workflows

### Using Make Commands

```bash
# Clean build artifacts
make clean

# Run all linting
make lint

# Run all tests
make test

# Format all code
make format

# Build package
make build

# Complete workflow
make all
```

### Using Tox (Multiple Python Versions)

```bash
# Test across all Python versions
tox

# Test specific Python version
tox -e py312

# Test specific environment
tox -e lint
tox -e coverage
```

### Using Pre-commit (Automated)

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run flake8 --all-files
```

## ⚡ Essential One-Liners

### Complete Quality Check
```bash
black src/ tests/ && isort src/ tests/ && flake8 src/ tests/ && mypy src/ && pytest --cov=src/ecoguard_ai
```

### Security & Vulnerability Check
```bash
bandit -r src/ && safety check && detect-secrets scan --all-files
```

### Package & CLI Verification
```bash
python -m build && pip install dist/*.whl --force-reinstall && ecoguard --version && ecoguard analyze examples/basic_usage.py
```

## 🚨 Critical Checks Before Push

**Must Pass:**
- [ ] All tests pass (`pytest`)
- [ ] No linting errors (`flake8`, `ruff`)
- [ ] Type checking passes (`mypy`)
- [ ] Code is formatted (`black`, `isort`)
- [ ] CLI works (`ecoguard --version`)
- [ ] Package builds (`python -m build`)
- [ ] Self-analysis runs (`ecoguard analyze src/`)

**Should Pass:**
- [ ] Security checks pass (`bandit`, `safety`)
- [ ] Coverage > 80% (`pytest --cov`)
- [ ] Documentation builds (`sphinx-build`)
- [ ] No secrets detected (`detect-secrets`)

## 🔧 Troubleshooting Common Issues

### Import Errors
```bash
# Reinstall in development mode
pip uninstall ecoguard-ai -y && pip install -e ".[dev]"
```

### Type Checking Errors
```bash
# Check mypy configuration
mypy --show-config
mypy --install-types  # Install missing type stubs
```

### Test Failures
```bash
# Run tests with verbose output
pytest -v -s

# Run specific failing test
pytest tests/test_specific.py::test_function -v
```

### Build Issues
```bash
# Clean build artifacts
rm -rf build/ dist/ *.egg-info/
python -m build --clean
```

## 📝 Git Commit Best Practices

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add new analysis rule for energy efficiency

- Implemented CPU usage pattern detection
- Added tests for new analyzer
- Updated documentation with examples
- Resolves #123"

# Push to feature branch
git push origin feature/energy-analysis
```

## 🎯 Quick Reference Commands

```bash
# Full pre-push workflow (copy-paste ready)
pip install -e ".[dev]" && \
black src/ tests/ examples/ && \
isort src/ tests/ examples/ && \
flake8 src/ tests/ examples/ && \
mypy src/ && \
pytest --cov=src/ecoguard_ai && \
bandit -r src/ && \
safety check && \
python -m build && \
ecoguard --version && \
ecoguard analyze examples/basic_usage.py --format table
```

---

**Note:** Always run these commands from the project root directory. If any command fails, fix the issues before pushing to maintain code quality standards.