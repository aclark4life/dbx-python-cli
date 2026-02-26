dbx-python-cli Documentation
============================

A command line tool for DBX Python development tasks. AI first. De-siloing happens here. Go from zero to hero in just a few minutes.

**Get started:** :doc:`introduction/installation` | :doc:`introduction/quick-start` | :doc:`introduction/overview`

What is dbx-python-cli?
-----------------------

dbx-python-cli is a unified command-line interface for managing Python development workflows across multiple related repositories. It provides tools for:

- 📦 **Repository Management** - Clone, sync, and organize related repositories
- 🐍 **Virtual Environments** - Group-level venvs with smart detection
- ⚡ **Fast Installation** - Dependency management powered by uv
- ✅ **Testing** - Run tests across repositories with consistent commands
- 🔧 **Task Automation** - Execute just commands and custom workflows

Feature Highlights
------------------

- 🤖 **AI-First Design** - Built with AI-assisted development workflows in mind
- 🔧 **Modern Tooling** - Uses the latest Python development tools and best practices
- 📦 **Fast Package Management** - Powered by `uv <https://github.com/astral-sh/uv>`_
- ✨ **Quality Focused** - Pre-commit hooks with `prek <https://github.com/aclark4life/prek>`_ and `ruff <https://github.com/astral-sh/ruff>`_
- 📚 **Well Documented** - Sphinx documentation with the beautiful Furo theme
- ✅ **Fully Tested** - Comprehensive test suite with pytest and coverage reporting

Quick Start
-----------

Install dbx-python-cli and get started in minutes:

.. code-block:: bash

   # Install via pipx
   pipx install git+https://github.com/aclark4life/dbx-python-cli.git

   # Initialize configuration
   dbx config init

   # Clone repositories by group
   dbx clone -g pymongo

   # Create virtual environment
   dbx env init -g pymongo

   # Install dependencies
   dbx install mongo-python-driver -e test

   # Run tests
   dbx test mongo-python-driver

See :doc:`introduction/quick-start` for a detailed walkthrough.

Documentation Sections
----------------------

.. toctree::
   :maxdepth: 2

   introduction/index
   features/index
   design/index
   api/index
   development/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
