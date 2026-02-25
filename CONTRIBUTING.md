# Contributing to dbx-python-cli

Thank you for your interest in contributing to dbx-python-cli! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [AI-Assisted Development](#ai-assisted-development)
- [Code Style and Quality](#code-style-and-quality)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) for package management
- Git for version control

### Setting Up Your Development Environment

1. **Fork and clone the repository:**

```bash
git clone https://github.com/YOUR_USERNAME/dbx-python-cli.git
cd dbx-python-cli
```

2. **Install development dependencies:**

```bash
uv pip install -e ".[dev]"
```

3. **Install pre-commit hooks:**

```bash
uvx prek install
```

## Development Workflow

### Running Tests

```bash
# Run all tests
just test

# Run tests with coverage
just test-cov

# Run specific test file
python -m pytest tests/test_open_command.py -v
```

### Code Formatting and Linting

```bash
# Format code with ruff
uvx ruff format .

# Check formatting
uvx ruff format --check .

# Run linter
uvx ruff check .

# Fix auto-fixable linting issues
uvx ruff check --fix .
```

### Building Documentation

```bash
# Build documentation
just docs

# Serve documentation locally
just docs-serve
```

## AI-Assisted Development

This project embraces AI-assisted development workflows. We recommend using **Augment Agent** or similar AI coding assistants to help with feature development, bug fixes, and code improvements.

### Using Augment Agent

When working with Augment Agent on this project, please reference this file at the start of your session:

```
Please read CONTRIBUTING.md for project guidelines and instructions.
```

### Instructions for AI Assistants

When contributing to this project, please follow these guidelines:

#### Code Changes

1. **Always search before editing**: Use `codebase-retrieval` to understand existing patterns and implementations before making changes
2. **Use package managers**: Always use `uv pip install/uninstall` instead of manually editing `pyproject.toml`
3. **Follow existing patterns**: Match the coding style and patterns used in similar commands/features
4. **Be conservative**: Respect the existing codebase structure and don't make unnecessary changes

#### Testing Requirements

1. **Write tests first**: For new features, write tests before or alongside implementation
2. **Update existing tests**: When modifying functionality, update affected tests
3. **Run full test suite**: Always run `python -m pytest` before committing
4. **Maintain coverage**: Aim to maintain or improve test coverage

#### Code Quality

1. **Format code**: Run `uvx ruff format .` before committing
2. **Fix linting errors**: Run `uvx ruff check --fix .` and address any remaining issues
3. **No f-strings without placeholders**: Use regular strings if there are no f-string placeholders
4. **Type hints**: Add type hints to function signatures where appropriate

#### Commit Guidelines

1. **Descriptive messages**: Write clear, descriptive commit messages
2. **Atomic commits**: Make focused commits that address one concern
3. **Test before commit**: Ensure all tests pass before committing
4. **Format before commit**: Ensure code is formatted before committing

#### Documentation

1. **Update docstrings**: Keep docstrings up-to-date with code changes
2. **Update docs**: Update Sphinx documentation for user-facing changes
3. **Add examples**: Include usage examples in docstrings and documentation

#### Project-Specific Instructions

<!--
Add project-specific instructions below this comment.
These instructions will be read by AI assistants in future sessions.

Examples:
- Specific architectural decisions or patterns to follow
- Known issues or workarounds
- Preferred libraries or approaches for certain tasks
- Domain-specific knowledge about MongoDB, PyMongo, etc.
- Common pitfalls to avoid
-->

**Current Project-Specific Instructions:**

1. **Fork workflow**: When repos are cloned with `--fork`, the `origin` remote points to the fork and `upstream` points to the original repo
2. **Group-based operations**: Many commands support `-g/--group` flag to operate on all repos in a group
3. **Verbose logging**: Use the `verbose` flag from context for detailed logging: `verbose = ctx.obj.get("verbose", False) if ctx.obj else False`
4. **Git operations**: Always use subprocess to run git commands, check return codes, and handle errors gracefully
5. **Config structure**: Configuration is in TOML format with `[repo.groups.GROUP_NAME]` sections containing repo lists

<!-- Add new instructions above this line -->

### For Human Developers

We encourage you to use AI assistants like Augment Agent to:

- **Add new features**: AI can help scaffold new commands and features following existing patterns
- **Fix bugs**: AI can help identify and fix issues while maintaining code quality
- **Write tests**: AI can generate comprehensive test cases
- **Improve documentation**: AI can help write clear documentation and examples
- **Refactor code**: AI can help improve code structure while preserving functionality

**Tip**: When asking an AI assistant to add a feature, provide context about:
- Similar existing features to use as reference
- Expected behavior and edge cases
- Testing requirements
- Documentation needs

## Code Style and Quality

### Python Style

- Follow PEP 8 guidelines
- Use [ruff](https://github.com/astral-sh/ruff) for formatting and linting
- Maximum line length: 88 characters (Black-compatible)
- Use type hints where appropriate

### Project Conventions

- Commands are organized in `src/dbx_python_cli/commands/`
- Each command has its own module (e.g., `open.py`, `clone.py`)
- Shared utilities go in `repo_utils.py` or similar utility modules
- Tests mirror the source structure in `tests/`
- Use Typer for CLI interface
- Use subprocess for git operations

## Testing

### Test Organization

- Unit tests in `tests/test_*.py`
- Integration tests in `tests/integration/`
- Use pytest fixtures for common setup
- Mock external dependencies (git, subprocess, etc.)

### Writing Tests

```python
def test_feature_name(tmp_path, mock_config):
    """Test description of what is being tested."""
    # Arrange
    # ... setup

    # Act
    result = runner.invoke(app, ["command", "args"])

    # Assert
    assert result.exit_code == 0
    assert "expected output" in result.stdout
```

## Documentation

- Main documentation in `docs/` using Sphinx
- API documentation auto-generated from docstrings
- Feature documentation in `docs/features/`
- Keep README.md up-to-date with major changes

## Submitting Changes

1. **Create a feature branch**: `git checkout -b feature/your-feature-name`
2. **Make your changes**: Follow the guidelines above
3. **Run tests**: Ensure all tests pass
4. **Format code**: Run ruff format and check
5. **Commit changes**: Use clear, descriptive commit messages
6. **Push to your fork**: `git push origin feature/your-feature-name`
7. **Open a Pull Request**: Describe your changes and link any related issues

### Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Ensure CI checks pass
- Be responsive to feedback and review comments

## Questions?

If you have questions or need help, please:
- Open an issue on GitHub
- Check existing documentation
- Ask in pull request comments

Thank you for contributing to dbx-python-cli! 🎉
