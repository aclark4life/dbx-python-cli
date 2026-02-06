dbx-python-cli Documentation
============================

A command line tool for DBX Python development tasks. AI first. De-siloing happens here.

About
-----

DBX Python is the MongoDB Database Experience Team for the Python driver. (Not affiliated with `Databricks <https://docs.databricks.com/aws/en/languages/python>`_.)

Features
--------

- 🤖 **AI-First Design** - Built with AI-assisted development workflows in mind
- 🔧 **Modern Tooling** - Uses the latest Python development tools and best practices
- 📦 **Fast Package Management** - Powered by `uv <https://github.com/astral-sh/uv>`_
- ✨ **Quality Focused** - Pre-commit hooks with `prek <https://github.com/aclark4life/prek>`_ and `ruff <https://github.com/astral-sh/ruff>`_
- 📚 **Well Documented** - Sphinx documentation with the beautiful Furo theme
- ✅ **Fully Tested** - Comprehensive test suite with pytest and coverage reporting

Installation
------------

Via pip (Coming Soon)
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Once released, you'll be able to install with:
   pip install dbx-python-cli

.. note::
   The package is not yet released to PyPI. For now, please see the Development section below.

Quick Start
-----------

.. code-block:: bash

   # Show help
   dbx --help

   # Show version
   dbx --version

Development
-----------

Getting Started
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/aclark4life/dbx-python-cli.git
   cd dbx-python-cli

   # Install the package (uses uv pip install -e .)
   just install

   # Install pre-commit hooks
   just install-hooks

The ``just install`` command uses `uv <https://github.com/astral-sh/uv>`_ under the hood to install the package in editable mode. If you need development dependencies, you can install them with just:

.. code-block:: bash

   just install-docs  # Documentation dependencies
   just install-test  # Testing dependencies

Or use uv directly:

.. code-block:: bash

   uv pip install -e ".[docs]"  # Documentation dependencies
   uv pip install -e ".[test]"  # Testing dependencies
   uv pip install -e ".[dev]"   # All development dependencies (docs + test)

Common Commands
~~~~~~~~~~~~~~~

This project uses `just <https://github.com/casey/just>`_ as a command runner. All commands have single-character aliases for convenience.

.. code-block:: bash

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

Running Tests
~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests with coverage
   just test

   # Run tests with verbose output
   just test-verbose

   # Generate coverage report
   just test-cov

Building Documentation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Build HTML documentation
   just docs

   # Serve documentation locally
   just docs-serve

   # Clean documentation build
   just docs-clean

Technology Stack
----------------

- **CLI Framework:** `Typer <https://typer.tiangolo.com/>`_ - Modern, intuitive CLI framework
- **Package Manager:** `uv <https://github.com/astral-sh/uv>`_ - Ultra-fast Python package installer
- **Task Runner:** `just <https://github.com/casey/just>`_ - Command runner with simple syntax
- **Pre-commit:** `prek <https://github.com/aclark4life/prek>`_ - Pre-commit hook manager
- **Linter/Formatter:** `ruff <https://github.com/astral-sh/ruff>`_ - Extremely fast Python linter
- **Documentation:** `Sphinx <https://www.sphinx-doc.org/>`_ with `Furo <https://github.com/pradyunsg/furo>`_ theme
- **Testing:** `pytest <https://pytest.org/>`_ with `pytest-cov <https://pytest-cov.readthedocs.io/>`_

API Reference
-------------

.. toctree::
   :maxdepth: 2

   api/modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
