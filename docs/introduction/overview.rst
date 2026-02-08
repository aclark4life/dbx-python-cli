Overview
========

This page provides a high-level overview of dbx-python-cli's features and capabilities.

Core Features
-------------

Repository Management
~~~~~~~~~~~~~~~~~~~~~

Manage multiple related repositories with ease:

- **Clone by Group** - Clone all repositories in a group with a single command
- **Sync Repositories** - Keep repositories up to date with upstream changes
- **Fork Workflow** - Support for working with forked repositories
- **List Repositories** - See all available repositories at a glance

See :doc:`../features/repo-management` for details.

Virtual Environment Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Group-level virtual environments for efficient dependency management:

- **Group-Level venvs** - One virtual environment per repository group
- **Python Version Selection** - Specify Python version when creating venvs
- **Smart Detection** - Automatically detects and uses the appropriate venv
- **List Environments** - See all virtual environments and their status
- **Remove Environments** - Clean up virtual environments when no longer needed

See :doc:`../design/venv-strategy` for the design rationale.

Dependency Installation
~~~~~~~~~~~~~~~~~~~~~~~

Fast, reliable dependency installation powered by uv:

- **Extras Support** - Install with optional dependencies (e.g., ``-e test,aws``)
- **Dependency Groups** - Support for PEP 735 dependency groups
- **Monorepo Support** - Install from specific directories in monorepos
- **Group Installation** - Install all repositories in a group at once
- **Show Options** - Preview what will be installed before running

See :doc:`../features/installation` for details.

Testing
~~~~~~~

Run tests across repositories with consistent commands:

- **Pytest Integration** - Run pytest with sensible defaults
- **Keyword Filtering** - Run specific tests with ``-k`` flag
- **Verbose Mode** - See detailed test output
- **Group Testing** - Specify which group's venv to use

See :doc:`../features/testing` for details.

Just Commands
~~~~~~~~~~~~~

Execute just commands in repositories:

- **Command Discovery** - Show available just commands
- **Argument Passing** - Pass arguments to just commands
- **Repository Context** - Run commands in the correct repository directory

See :doc:`../features/just-commands` for details.

Command Structure
-----------------

dbx-python-cli uses a hierarchical command structure:

.. code-block:: text

   dbx [global-options] <command> [command-options] [arguments]

Global Options
~~~~~~~~~~~~~~

Available for all commands:

- ``-v, --verbose`` - Enable verbose output
- ``-h, --help`` - Show help message
- ``--version`` - Show version information

Commands
~~~~~~~~

Main command groups:

- ``repo`` - Repository management (clone, sync, list, init)
- ``env`` - Virtual environment management (init, list, remove)
- ``install`` - Dependency installation
- ``test`` - Run tests
- ``just`` - Run just commands

See :doc:`../features/global-options` for details on global options.

Configuration
-------------

Configuration File
~~~~~~~~~~~~~~~~~~

dbx-python-cli uses a TOML configuration file located at:

- **macOS/Linux**: ``~/.config/dbx-python-cli/config.toml``
- **Windows**: ``%APPDATA%\dbx-python-cli\config.toml``

Example configuration:

.. code-block:: toml

   [repo]
   base_dir = "~/Developer/mongodb"
   # fork_user = "your-github-username"  # Optional

   [repo.groups.pymongo]
   repos = [
       "git@github.com:mongodb/mongo-python-driver.git",
       "git@github.com:mongodb/specifications.git",
   ]

   [repo.groups.langchain]
   repos = [
       "git@github.com:langchain-ai/langchain-mongodb.git",
   ]

Repository Groups
~~~~~~~~~~~~~~~~~

Repositories are organized into groups. Each group:

- Has its own directory under ``base_dir``
- Can have a shared virtual environment
- Can be cloned, synced, or installed as a unit

Directory Structure
-------------------

Typical directory structure after setup:

.. code-block:: text

   ~/Developer/mongodb/              # base_dir
   ├── pymongo/                      # Group directory
   │   ├── .venv/                    # Group-level virtual environment
   │   ├── mongo-python-driver/     # Repository
   │   ├── specifications/          # Repository
   │   └── drivers-evergreen-tools/ # Repository
   └── langchain/                    # Another group
       ├── .venv/                    # Separate venv for this group
       └── langchain-mongodb/       # Repository

Design Philosophy
-----------------

**Standalone Installation**
   Installed globally, not tied to any specific repository. See :doc:`../design/standalone-installation`.

**Group-Based Organization**
   Repositories organized into logical groups with shared environments. See :doc:`../design/venv-strategy`.

**Modern Tooling**
   Uses the latest Python development tools for speed and reliability.

**AI-First**
   Designed to work well with AI assistants and automated workflows.

**Developer Experience**
   Focus on making common tasks simple with clear, helpful output.

Technology Stack
----------------

dbx-python-cli is built with:

- **CLI Framework**: `Typer <https://typer.tiangolo.com/>`_ - Modern, intuitive CLI framework
- **Package Manager**: `uv <https://github.com/astral-sh/uv>`_ - Ultra-fast Python package installer
- **Task Runner**: `just <https://github.com/casey/just>`_ - Command runner with simple syntax
- **Linter/Formatter**: `ruff <https://github.com/astral-sh/ruff>`_ - Extremely fast Python linter
- **Testing**: `pytest <https://pytest.org/>`_ - Feature-rich testing framework
- **Documentation**: `Sphinx <https://www.sphinx-doc.org/>`_ with `Furo <https://github.com/pradyunsg/furo>`_ theme

Next Steps
----------

- :doc:`installation` - Install dbx-python-cli
- :doc:`quick-start` - Get started with a quick tutorial
- :doc:`../features/index` - Explore all features in detail
- :doc:`../development/index` - Contribute to the project
