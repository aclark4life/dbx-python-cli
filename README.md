# dbx-python-cli

> A command line tool for DBX Python development tasks. AI first. De-siloing happens here. Inspired by [django-mongodb-cli](https://github.com/mongodb-labs/django-mongodb-cli).

[![CI](https://github.com/aclark4life/dbx-python-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/aclark4life/dbx-python-cli/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/aclark4life/dbx-python-cli/branch/main/graph/badge.svg)](https://codecov.io/gh/aclark4life/dbx-python-cli)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## About

DBX Python is the MongoDB Database Experience Team for the MongoDB Python driver.

> **Note:** This is not [Databricks for Python developers](https://docs.databricks.com/aws/en/languages/python).

## Feature Highlights

- 🤖 **AI-First Design** - Built with AI-assisted development workflows in mind
- 🔧 **Modern Tooling** - Uses the latest Python development tools and best practices
- 📦 **Fast Package Management** - Powered by [uv](https://github.com/astral-sh/uv)
- ✨ **Quality Focused** - Pre-commit hooks with [prek](https://github.com/aclark4life/prek) and [ruff](https://github.com/astral-sh/ruff)
- 📚 **Well Documented** - Sphinx documentation with the beautiful Furo theme
- ✅ **Fully Tested** - Comprehensive test suite with pytest and coverage reporting

See the [full documentation](https://dbx-python-cli.readthedocs.io/) for detailed feature documentation.

## Installation

### Via pipx (Recommended)

```bash
# Install directly from GitHub
pipx install git+https://github.com/aclark4life/dbx-python-cli.git
```

This will install `dbx-python-cli` globally and make the `dbx` command available in your terminal.

## Quick Start

```bash
# Initialize configuration
dbx config init

# Clone repositories by group
dbx clone -g pymongo

# List available repositories
dbx list

# Install dependencies in a repository
dbx install mongo-python-driver -e test

# Install with multiple extras
dbx install mongo-python-driver -e test -e aws

# Install with dependency groups
dbx install mongo-python-driver -e test --dependency-groups dev,test

# Install all repositories in a group
dbx install -g pymongo

# Install all repos in a group with extras
dbx install -g pymongo -e test --dependency-groups dev

# Use a different group's venv for a single repo
dbx install mongo-python-driver -g pymongo

# Run tests in a repository
dbx test mongo-python-driver

# Run tests matching a keyword expression
dbx test mongo-python-driver -k "test_connection"

# Run just commands in a repository
dbx just mongo-python-driver          # Show available just commands
dbx just mongo-python-driver lint     # Run 'just lint'
dbx just mongo-python-driver test -v  # Run 'just test -v'

# Fetch remote updates
dbx fetch mongo-python-driver         # Fetch updates for a single repo
dbx fetch -g pymongo                  # Fetch updates for all repos in a group
dbx fetch --prune mongo-python-driver # Fetch and prune stale remote branches

# View git branches in repositories
dbx branch mongo-python-driver        # Show branches in a repo
dbx branch mongo-python-driver -a     # Show all branches (including remote)
dbx branch -g pymongo                 # Show branches in all repos in a group
dbx branch -g pymongo -a              # Show all branches in all repos in a group
dbx branch -p myproject               # Show branches in a project

# Common workflow: fetch first, then view all branches
dbx fetch -g django
dbx branch -g django -a

# Use verbose mode for more detailed output
dbx -v install mongo-python-driver -e test
dbx -v test mongo-python-driver
dbx -v clone -g pymongo
dbx -v just mongo-python-driver lint
dbx -v branch -g pymongo
```

## Development

### Getting Started

```bash
# Clone the repository
git clone https://github.com/aclark4life/dbx-python-cli.git
cd dbx-python-cli

# Install the package (uses uv pip install -e .)
just install

# Install pre-commit hooks
just install-hooks
```

The `just install` command uses [uv](https://github.com/astral-sh/uv) under the hood to install the package in editable mode. If you need development dependencies, you can install them with just:

```bash
just install-docs  # Documentation dependencies
just install-test  # Testing dependencies
```

Or use uv directly:

```bash
uv pip install -e ".[docs]"  # Documentation dependencies
uv pip install -e ".[test]"  # Testing dependencies
uv pip install -e ".[dev]"   # All development dependencies (docs + test)
```

### Command Runner

This project uses [just](https://github.com/casey/just) as a command runner. All commands have single-character aliases for convenience.

### Common Commands

```bash
# Install the package
just install      # or: just i

# Run tests
just test         # or: just t

# Build documentation
just docs         # or: just d

# Format code
just format       # or: just f

# Run linter
just lint         # or: just l

# Run pre-commit hooks
just hooks-run    # or: just h

# Build the package
just build        # or: just b

# Clean build artifacts
just clean        # or: just c
```

### Running Tests

```bash
# Run all tests with coverage
just test

# Run tests with verbose output
just test-verbose

# Generate coverage report
just test-cov
```

### Building Documentation

```bash
# Build HTML documentation
just docs

# Serve documentation locally
just docs-serve

# Clean documentation build
just docs-clean
```

## Technology Stack

- **CLI Framework:** [Typer](https://typer.tiangolo.com/) - Modern, intuitive CLI framework
- **Package Manager:** [uv](https://github.com/astral-sh/uv) - Ultra-fast Python package installer
- **Task Runner:** [just](https://github.com/casey/just) - Command runner with simple syntax
- **Pre-commit:** [prek](https://github.com/aclark4life/prek) - Pre-commit hook manager
- **Linter/Formatter:** [ruff](https://github.com/astral-sh/ruff) - Extremely fast Python linter
- **Documentation:** [Sphinx](https://www.sphinx-doc.org/) with [Furo](https://github.com/pradyunsg/furo) theme
- **Testing:** [pytest](https://pytest.org/) with [pytest-cov](https://pytest-cov.readthedocs.io/)

## Project Structure

```
dbx-python-cli/
├── src/dbx_python_cli/  # Source code
│   ├── __init__.py      # Package initialization
│   └── cli.py           # CLI implementation
├── tests/               # Test suite
│   ├── conftest.py      # Pytest configuration
│   ├── test_cli.py      # CLI tests
│   └── test_version.py  # Version tests
├── docs/                # Sphinx documentation
│   ├── conf.py          # Sphinx configuration
│   └── index.rst        # Documentation index
├── pyproject.toml       # Project configuration
├── justfile             # Task runner commands
└── README.md            # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Install pre-commit hooks (`just install-hooks`)
4. Make your changes
5. Run tests (`just test`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Links

- **Documentation:** [Read the Docs](https://dbx-python-cli.readthedocs.io/)
- **Source Code:** [GitHub](https://github.com/aclark4life/dbx-python-cli)
- **Issue Tracker:** [GitHub Issues](https://github.com/aclark4life/dbx-python-cli/issues)

---

Made with ❤️ by MongoDB DBX Python
