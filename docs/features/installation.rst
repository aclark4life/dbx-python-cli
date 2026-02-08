Installing Dependencies
=======================

Install Dependencies in Repositories
-------------------------------------

Install dependencies in any cloned repository using ``uv pip install``:

.. code-block:: bash

   # List all available repositories
   dbx install --list

   # Install a repository in editable mode
   dbx install mongo-python-driver

   # Install with extras
   dbx install mongo-python-driver -e test

   # Install with multiple extras
   dbx install mongo-python-driver -e test,aws

   # Install with dependency groups
   dbx install mongo-python-driver --dependency-groups dev,test

   # Combine extras and dependency groups
   dbx install mongo-python-driver -e test,aws --dependency-groups dev

   # Use -g to specify which group (when repo exists in multiple groups)
   dbx install mongo-python-driver -g pymongo

   # Short forms
   dbx install -l  # list
   dbx install mongo-python-driver -e test  # install with test extras
   dbx install mongo-python-driver -e test --dependency-groups dev  # install with test extras and dev dependency group

The ``install`` command will:

1. Find the repository by name across all cloned groups
2. Run ``uv pip install -e .`` (or with extras if specified)
3. Optionally install dependency groups with ``--dependency-groups`` flag
4. Display installation results

Example Output
--------------

.. code-block:: bash

   $ dbx install --list
   Available repositories:

     • mongo-python-driver (pymongo)
     • specifications (pymongo)
     • django (django)
     • django-mongodb-backend (django)

   $ dbx install mongo-python-driver -e test
   Installing dependencies in ~/Developer/mongodb/pymongo/mongo-python-driver...

   ✅ Package installed successfully

   $ dbx install mongo-python-driver -e test,aws --dependency-groups dev
   Installing dependencies in ~/Developer/mongodb/pymongo/mongo-python-driver...

   ✅ Package installed successfully

   Installing dependency groups: dev...

   ✅ Dependency group 'dev' installed successfully

Monorepo Support
----------------

``dbx`` supports installing from monorepos (repositories with multiple packages). For example, ``langchain-mongodb`` is a monorepo containing three packages:

- ``libs/langchain-mongodb/``
- ``libs/langgraph-checkpoint-mongodb/``
- ``libs/langgraph-store-mongodb/``

When you install a monorepo, ``dbx`` automatically detects the ``install_dirs`` configuration and installs each package separately:

.. code-block:: bash

   $ dbx install langchain-mongodb

   Monorepo detected: installing 3 packages...

     → Installing from libs/langchain-mongodb/...
     ✅ libs/langchain-mongodb/ installed successfully

     → Installing from libs/langgraph-checkpoint-mongodb/...
     ✅ libs/langgraph-checkpoint-mongodb/ installed successfully

     → Installing from libs/langgraph-store-mongodb/...
     ✅ libs/langgraph-store-mongodb/ installed successfully

   ✅ All packages in langchain-mongodb installed successfully!

You can also install monorepos with extras and dependency groups:

.. code-block:: bash

   # Install all packages with dev dependencies
   dbx install langchain-mongodb --dependency-groups dev

   # Install all packages with extras
   dbx install langchain-mongodb -e test

Configuring Monorepos
~~~~~~~~~~~~~~~~~~~~~

Monorepos are configured in ``config.toml`` using the ``install_dirs`` setting:

.. code-block:: toml

   [repo.groups.langchain]
   repos = [
       "git@github.com:langchain-ai/langchain-mongodb.git",
   ]

   # Monorepo configuration: specify install directories
   [repo.groups.langchain.install_dirs]
   langchain-mongodb = [
       "libs/langchain-mongodb/",
       "libs/langgraph-checkpoint-mongodb/",
       "libs/langgraph-store-mongodb/",
   ]

Each directory in ``install_dirs`` must contain a ``pyproject.toml`` or ``setup.py`` file.

Install Command Options
-----------------------

The ``install`` command uses ``uv pip install`` to install dependencies:

- ``-e`` / ``--extras``: Comma-separated list of extras to install (e.g., 'test', 'dev', 'aws')
- ``--dependency-groups``: Comma-separated list of dependency groups to install (e.g., 'dev', 'test')
- ``-g`` / ``--group``: Specify which group to use (useful when a repo exists in multiple groups)

This is useful when:

- You need to install dependencies for the first time
- Dependencies have been updated
- You want to install specific extras or dependency groups
- You're working with monorepos that have multiple packages

Requirements
------------

- The repository must be cloned first using ``dbx repo clone``
- The repository must have a ``pyproject.toml`` or ``setup.py``
- For monorepos, each ``install_dirs`` directory must have a ``pyproject.toml`` or ``setup.py``
