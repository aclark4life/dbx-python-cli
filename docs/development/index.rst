Development
===========

This section covers development workflows for contributing to dbx-python-cli.

.. toctree::
   :maxdepth: 2

   setup
   testing
   documentation
   contributing

Overview
--------

dbx-python-cli is built with modern Python development tools and practices:

- **CLI Framework:** `Typer <https://typer.tiangolo.com/>`_ - Modern, intuitive CLI framework
- **Package Manager:** `uv <https://github.com/astral-sh/uv>`_ - Ultra-fast Python package installer
- **Task Runner:** `just <https://github.com/casey/just>`_ - Command runner with simple syntax
- **Pre-commit:** `prek <https://github.com/aclark4life/prek>`_ - Pre-commit hook manager
- **Linter/Formatter:** `ruff <https://github.com/astral-sh/ruff>`_ - Extremely fast Python linter
- **Documentation:** `Sphinx <https://www.sphinx-doc.org/>`_ with `Furo <https://github.com/pradyunsg/furo>`_ theme
- **Testing:** `pytest <https://pytest.org/>`_ with `pytest-cov <https://pytest-cov.readthedocs.io/>`_

Quick Start
-----------

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/aclark4life/dbx-python-cli.git
   cd dbx-python-cli

   # Install the package (uses uv pip install -e .)
   just install

   # Install pre-commit hooks
   just install-hooks

   # Run tests
   just test

   # Build documentation
   just docs

See the following sections for detailed information on each development workflow.
