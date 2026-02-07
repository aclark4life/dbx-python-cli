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
   dbx install mongo-python-driver -g dev,test

   # Combine extras and groups
   dbx install mongo-python-driver -e test,aws -g dev

   # Short forms
   dbx install -l  # list
   dbx install mongo-python-driver -e test  # install with test extras
   dbx install mongo-python-driver -e test -g dev  # install with test extras and dev group

The ``install`` command will:

1. Find the repository by name across all cloned groups
2. Run ``uv pip install -e .`` (or with extras if specified)
3. Optionally install dependency groups with ``--group`` flag
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
   Installing dependencies in ~/Developer/dbx-repos/pymongo/mongo-python-driver...

   ✅ Package installed successfully

   $ dbx install mongo-python-driver -e test,aws -g dev
   Installing dependencies in ~/Developer/dbx-repos/pymongo/mongo-python-driver...

   ✅ Package installed successfully

   Installing dependency groups: dev...

   ✅ Group 'dev' installed successfully

Install Command Options
-----------------------

The ``install`` command uses ``uv pip install`` to install dependencies:

- ``-e`` / ``--extras``: Comma-separated list of extras to install (e.g., 'test', 'dev', 'aws')
- ``-g`` / ``--groups``: Comma-separated list of dependency groups to install (e.g., 'dev', 'test')

This is useful when:

- You need to install dependencies for the first time
- Dependencies have been updated
- You want to install specific extras or dependency groups

Requirements
------------

- The repository must be cloned first using ``dbx repo clone``
- The repository must have a ``pyproject.toml`` or ``setup.py``
