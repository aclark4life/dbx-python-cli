Status Command
==============

Show Git Status of Repositories
--------------------------------

The ``dbx status`` command shows the git status of repositories, making it easy to check the working tree state across multiple repositories.

Basic Usage
-----------

.. code-block:: bash

   # Show status of a single repository
   dbx status mongo-python-driver

   # Show status of all repositories in a group
   dbx status -g pymongo

   # Show short-format status
   dbx status --short mongo-python-driver

   # List all available repositories
   dbx status --list

Command Options
---------------

The ``status`` command supports the following options:

* ``<repo_name>`` - Repository name to show status for
* ``-g, --group <group_name>`` - Show status for all repositories in a group
* ``-s, --short`` - Show short-format status output (equivalent to ``git status --short``)
* ``-l, --list`` - Show repository status (cloned vs available)

Examples
--------

Show Status of a Single Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ dbx status mongo-python-driver
   📊 mongo-python-driver:
   On branch main
   Your branch is up to date with 'origin/main'.

   nothing to commit, working tree clean

Show Status of All Repositories in a Group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ dbx status -g pymongo
   Showing status for 2 repository(ies) in group 'pymongo':

   📊 mongo-python-driver:
   On branch main
   Your branch is up to date with 'origin/main'.

   nothing to commit, working tree clean

   📊 specifications:
   On branch master
   Your branch is up to date with 'origin/master'.

   nothing to commit, working tree clean

Show Short-Format Status
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``--short`` flag provides a compact view of changes:

.. code-block:: bash

   $ dbx status --short mongo-python-driver
   📊 mongo-python-driver:
    M src/pymongo/collection.py
   ?? new_file.py

List Available Repositories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ dbx status --list
   Base directory: ~/Developer/dbx-repos

   Repository status:

   pymongo
   ├── ✓ mongo-python-driver
   └── ✓ specifications

   django
   └── ✓ django-mongodb-backend

   Legend: ✓ = cloned, ○ = available to clone, ? = cloned but not in config

Verbose Mode
------------

Use the ``-v`` / ``--verbose`` flag to see detailed information about what the command is doing:

.. code-block:: bash

   $ dbx -v status mongo-python-driver
   [verbose] Using base directory: ~/Developer/dbx-repos
   [verbose] Config: {...}

   📊 mongo-python-driver:
   [verbose] Running command: git status
   [verbose] Working directory: ~/Developer/dbx-repos/pymongo/mongo-python-driver

   On branch main
   Your branch is up to date with 'origin/main'.

   nothing to commit, working tree clean

Use Cases
---------

Check Working Tree State
~~~~~~~~~~~~~~~~~~~~~~~~

Quickly check if you have uncommitted changes:

.. code-block:: bash

   dbx status mongo-python-driver

Check Multiple Repositories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check the status of all repositories in a group to see which ones have uncommitted changes:

.. code-block:: bash

   dbx status -g pymongo

Quick Overview with Short Format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get a compact view of changes across repositories:

.. code-block:: bash

   dbx status --short -g pymongo

Requirements
------------

- The repository must be cloned first using ``dbx clone``
- The repository must be a valid git repository (contains a ``.git`` directory)

Related Commands
----------------

- :doc:`repo-management` - Clone and sync repositories
- ``dbx branch`` - Show git branches
- ``dbx log`` - Show git log
- ``dbx remote`` - Show git remotes
