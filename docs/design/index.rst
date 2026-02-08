Design Decisions
================

This section documents key design decisions made in the development of dbx-python-cli.

.. toctree::
   :hidden:

   standalone-installation
   git-operations
   venv-strategy

Standalone Installation
-----------------------

We install dbx-python-cli as a standalone tool, not requiring a clone of the CLI repository. See :doc:`standalone-installation` for details.

Git Operations
--------------

We use subprocess with git CLI instead of GitPython for simplicity and reliability. See :doc:`git-operations` for details.

Virtual Environment Strategy
-----------------------------

We use group-level virtual environments managed with uv. See :doc:`venv-strategy` for details.
