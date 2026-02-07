Design Decisions
================

This section documents key design decisions made in the development of dbx-python-cli.

.. toctree::
   :hidden:

   git-operations
   venv-strategy

Git Operations
--------------

We use subprocess with git CLI instead of GitPython for simplicity and reliability. See :doc:`git-operations` for details.

Virtual Environment Strategy
-----------------------------

We use group-level virtual environments managed with uv. See :doc:`venv-strategy` for details.
