dbx Documentation
=================

A command line tool for DBX Python development tasks. AI first. De-siloing happens here.

DBX Python is the MongoDB Database Experience Team for the Python driver.

.. note::
   DBX in this context refers to the MongoDB Database Experience team, not Databricks.

Installation
------------

Install the package using uv:

.. code-block:: bash

   uv pip install -e .

Or using pip:

.. code-block:: bash

   pip install -e .

Usage
-----

The ``dbx`` command provides a CLI interface for development tasks:

.. code-block:: bash

   dbx --help
   dbx --version

Development
-----------

This project uses:

- **Typer** for the CLI framework
- **Just** for task automation
- **Prek** for pre-commit hooks
- **Ruff** for linting and formatting
- **Sphinx** with Furo theme for documentation

Quick Start
~~~~~~~~~~~

.. code-block:: bash

   # Install the package
   just install

   # Run the CLI
   just run

   # Build documentation
   just docs

   # Run pre-commit hooks
   just hooks-run

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

