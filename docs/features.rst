Features
========

This page provides detailed documentation for all dbx-python-cli features.

Repository Management
---------------------

The ``dbx repo`` command provides repository management functionality for cloning and managing groups of related repositories.

Clone Repositories by Group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone repositories from predefined groups:

.. code-block:: bash

   # Clone pymongo repositories
   dbx repo clone -g pymongo

   # Clone langchain repositories
   dbx repo clone -g langchain

   # Clone django repositories
   dbx repo clone -g django

**Available Groups:**

- ``pymongo`` - MongoDB Python driver repositories
- ``langchain`` - LangChain framework repositories
- ``django`` - Django web framework repositories

**Configuration:**

Repository groups are defined in ``pyproject.toml`` under ``[tool.dbx.repo.groups]``. The default base directory for cloning is ``~/repos``, which can be customized in the configuration:

.. code-block:: toml

   [tool.dbx.repo]
   base_dir = "~/repos"

   [tool.dbx.repo.groups.pymongo]
   repos = [
       "https://github.com/mongodb/mongo-python-driver.git",
   ]

**Features:**

- Clones all repositories in a group to the configured base directory
- Skips repositories that already exist locally
- Provides clear progress feedback with emoji indicators
- Handles errors gracefully and continues with remaining repositories
