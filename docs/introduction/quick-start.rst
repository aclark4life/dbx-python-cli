Quick Start
===========

This guide will help you get started with dbx-python-cli in just a few minutes.

Step 1: Initialize Configuration
---------------------------------

First, initialize the configuration file:

.. code-block:: bash

   dbx config init

This creates a configuration file at ``~/.config/dbx-python-cli/config.toml`` with default settings.

The default configuration includes:

- Base directory: ``~/Developer/mongodb``
- Pre-configured repository groups (pymongo, langchain, etc.)

You can edit this file to customize your setup.

Step 2: Clone Repositories
---------------------------

Clone a group of related repositories:

.. code-block:: bash

   # Clone the pymongo group
   dbx clone -g pymongo

This will clone all repositories in the pymongo group to ``~/Developer/mongodb/pymongo/``.

To see available groups:

.. code-block:: bash

   dbx clone --list

Step 3: Create a Virtual Environment
-------------------------------------

Create a virtual environment for the group:

.. code-block:: bash

   # Create venv for pymongo group
   dbx env init -g pymongo

This creates a virtual environment at ``~/Developer/mongodb/pymongo/.venv``.

To specify a Python version:

.. code-block:: bash

   dbx env init -g pymongo --python 3.11

Step 4: Install Dependencies
-----------------------------

Install dependencies for a repository:

.. code-block:: bash

   # Install dependencies for mongo-python-driver
   dbx install mongo-python-driver

To install with extras:

.. code-block:: bash

   # Install with test extras
   dbx install mongo-python-driver -e test

   # Install with multiple extras
   dbx install mongo-python-driver -e test,aws,encryption

Step 5: Run Tests
-----------------

Run tests for a repository:

.. code-block:: bash

   # Run all tests
   dbx test mongo-python-driver

   # Run tests matching a keyword
   dbx test mongo-python-driver -k "test_connection"

Working with Django Projects
-----------------------------

Create and manage Django projects with MongoDB backend:

.. code-block:: bash

   # Create a new project
   dbx project add myproject

   # Create a virtual environment for projects
   dbx env init -g projects

   # Install the project
   dbx install myproject

   # Run the project (defaults to newest project)
   dbx project run

   # Create a superuser (defaults to newest project)
   dbx project su

   # Run Django management commands (defaults to newest project)
   dbx project manage shell
   dbx project manage migrate

.. note::

   **Convenience Feature**: Most project commands default to the newest project when no name is specified. This makes it faster to work with your current project without typing the name repeatedly.

Common Workflows
----------------

List Everything
~~~~~~~~~~~~~~~

See what's available:

.. code-block:: bash

   # List all cloned repositories
   dbx -l

   # List all virtual environments
   dbx env list

   # List repositories for install
   dbx install --list

   # List repositories for testing
   dbx test --list

Run Just Commands
~~~~~~~~~~~~~~~~~

If a repository has a ``justfile``, you can run just commands:

.. code-block:: bash

   # Show available just commands
   dbx just mongo-python-driver

   # Run a specific just command
   dbx just mongo-python-driver lint

   # Run just command with arguments
   dbx just mongo-python-driver test -v

Sync Repositories
~~~~~~~~~~~~~~~~~

Keep your repositories up to date:

.. code-block:: bash

   # Sync a single repository
   dbx sync mongo-python-driver

   # Sync all repositories in a group
   dbx sync -g pymongo

View Git Branches
~~~~~~~~~~~~~~~~~

View branches across repositories:

.. code-block:: bash

   # View branches in a single repository
   dbx branch mongo-python-driver

   # View all branches (including remote)
   dbx branch mongo-python-driver -a

   # View branches in all repositories in a group
   dbx branch -g pymongo

Working with Multiple Groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can work with multiple repository groups:

.. code-block:: bash

   # Clone langchain group
   dbx clone -g langchain

   # Create venv for langchain
   dbx env init -g langchain

   # Install dependencies
   dbx install langchain-mongodb -g langchain

Verbose Mode
~~~~~~~~~~~~

Use ``-v`` or ``--verbose`` for detailed output:

.. code-block:: bash

   dbx -v install mongo-python-driver
   dbx --verbose test mongo-python-driver

Next Steps
----------

Now that you're familiar with the basics, explore:

- :doc:`../features/index` - Detailed feature documentation
- :doc:`overview` - High-level overview of all features
- :doc:`../design/index` - Design decisions and architecture
- :doc:`../development/index` - Contributing to dbx-python-cli
