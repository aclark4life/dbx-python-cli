Features
========

This page provides detailed documentation for all dbx-python-cli features.

Repository Management
---------------------

The ``dbx repo`` command provides repository management functionality for cloning and managing groups of related repositories.

Initialize Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

Before using the repo commands, initialize your configuration file:

.. code-block:: bash

   # Create user configuration file at ~/.config/dbx-python-cli/config.toml
   dbx repo init

This creates a configuration file with default repository groups that you can customize.

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

**Available Groups (Default):**

- ``pymongo`` - MongoDB Python driver repositories (PyMongo, Specifications)
- ``langchain`` - LangChain framework repositories
- ``django`` - Django web framework repositories (Django, django-mongodb-backend)

**Configuration:**

Repository groups are defined in ``~/.config/dbx-python-cli/config.toml``. The default base directory for cloning is ``~/Developer/dbx-repos``, which can be customized.

Repositories are cloned into subdirectories named after their group. For example, the ``pymongo`` group will be cloned to ``~/Developer/dbx-repos/pymongo/``.

.. code-block:: toml

   [repo]
   base_dir = "~/Developer/dbx-repos"

   [repo.groups.pymongo]
   repos = [
       "https://github.com/mongodb/mongo-python-driver.git",
       "https://github.com/mongodb/specifications.git",
   ]

   [repo.groups.django]
   repos = [
       "https://github.com/django/django.git",
       "https://github.com/mongodb-labs/django-mongodb-backend.git",
   ]

   [repo.groups.custom]
   repos = [
       "https://github.com/your-org/your-repo.git",
   ]

You can add your own custom groups by editing the configuration file.

**Features:**

- User-specific configuration file (works with pip-installed package)
- Clones all repositories in a group to the configured base directory
- Skips repositories that already exist locally
- Provides clear progress feedback with emoji indicators
- Handles errors gracefully and continues with remaining repositories
- Easy to add custom repository groups

Testing
-------

Run Tests in Repositories
~~~~~~~~~~~~~~~~~~~~~~~~~~

Run pytest in any cloned repository:

.. code-block:: bash

   # List all available repositories
   dbx test --list

   # Run tests in a specific repository
   dbx test mongo-python-driver

   # Install test extras before running tests
   dbx test mongo-python-driver --install test

   # Install dev extras before running tests
   dbx test mongo-python-driver --install dev

   # Run tests matching a keyword expression
   dbx test mongo-python-driver --keyword "test_connection"

   # Short forms
   dbx test -l  # list
   dbx test mongo-python-driver -i test  # install test extras and run tests
   dbx test mongo-python-driver -i dev  # install dev extras and run tests
   dbx test mongo-python-driver -k "test_auth"  # filter tests

   # Combine flags
   dbx test mongo-python-driver -i test -k "test_connection"

The ``test`` command will:

1. Find the repository by name across all cloned groups
2. Optionally install extras with ``-i`` / ``--install`` flag (specify which extra, e.g., 'test', 'dev')
3. Run ``pytest`` in the repository directory (with optional ``-k`` filter)
4. Display the test results

**Example:**

.. code-block:: bash

   $ dbx test --list
   Available repositories in ~/Developer/dbx-repos:

     [django] django
     [django] django-mongodb-backend
     [pymongo] mongo-python-driver
     [pymongo] specifications

   $ dbx test mongo-python-driver
   Running pytest in ~/Developer/dbx-repos/pymongo/mongo-python-driver...

   ============================= test session starts ==============================
   ...
   ✅ Tests passed in mongo-python-driver

   $ dbx test mongo-python-driver -i test
   Installing 'test' extras in ~/Developer/dbx-repos/pymongo/mongo-python-driver...

   ✅ 'test' extras installed successfully

   Running pytest in ~/Developer/dbx-repos/pymongo/mongo-python-driver...

   ============================= test session starts ==============================
   ...
   ✅ Tests passed in mongo-python-driver

**Install Extras:**

The ``-i`` / ``--install`` flag accepts an extra name (e.g., 'test', 'dev', 'docs') and will run ``uv pip install -e ".[<extra>]"`` in the repository directory before running tests. This is useful when:

- You need to install test dependencies for the first time
- Test dependencies have been updated
- You want to ensure all test extras are up to date

If the installation fails, a warning is displayed but the test run continues.

**Filter Tests by Keyword:**

The ``-k`` / ``--keyword`` flag passes a keyword expression to pytest's ``-k`` option to filter which tests to run. This is useful for:

- Running only tests matching a specific pattern (e.g., ``-k "test_connection"``)
- Running tests from a specific class (e.g., ``-k "TestAuth"``)
- Using boolean expressions (e.g., ``-k "test_auth and not test_slow"``)

The keyword expression is passed directly to pytest, so all pytest ``-k`` syntax is supported.

**Requirements:**

- The repository must be cloned first using ``dbx repo clone``
- For the ``-i`` flag: The repository must have a ``pyproject.toml`` or ``setup.py`` with test extras defined
- For the ``-k`` flag: The repository must have pytest installed
