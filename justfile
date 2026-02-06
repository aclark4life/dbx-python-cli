# Default recipe to display help information
default:
    @just --list

# Install the package in editable mode
install:
    pip install -e .

# Install development dependencies
install-dev:
    pip install -e ".[dev]"

# Build the package
build:
    python -m build

# Clean build artifacts
clean:
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info
    rm -rf src/*.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Run the CLI with --help
run:
    dbx --help

# Run the CLI with --version
version:
    dbx --version

# Uninstall the package
uninstall:
    pip uninstall -y dbx

# Reinstall the package (clean install)
reinstall: uninstall install

# Format code (placeholder for future formatter)
format:
    @echo "No formatter configured yet"

# Lint code (placeholder for future linter)
lint:
    @echo "No linter configured yet"

# Run tests (placeholder for future tests)
test:
    @echo "No tests configured yet"

