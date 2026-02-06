# Default recipe to display help information
default:
    @just --list

# Install the package in editable mode
install:
    pip install -e .

# Alias for install
alias i := install

# Install development dependencies
install-dev:
    pip install -e ".[dev]"

# Build the package
build:
    python -m build

# Alias for build
alias b := build

# Clean build artifacts
clean:
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info
    rm -rf src/*.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Alias for clean
alias c := clean

# Run the CLI with --help
run:
    dbx --help

# Alias for run
alias r := run

# Run the CLI with --version
version:
    dbx --version

# Alias for version
alias v := version

# Uninstall the package
uninstall:
    pip uninstall -y dbx

# Alias for uninstall
alias u := uninstall

# Reinstall the package (clean install)
reinstall: uninstall install

# Format code (placeholder for future formatter)
format:
    @echo "No formatter configured yet"

# Alias for format
alias f := format

# Lint code (placeholder for future linter)
lint:
    @echo "No linter configured yet"

# Alias for lint
alias l := lint

# Run tests (placeholder for future tests)
test:
    @echo "No tests configured yet"

# Alias for test
alias t := test

