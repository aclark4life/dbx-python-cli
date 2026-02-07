Testing
=======

Run Tests in Repositories
--------------------------

Run pytest in any cloned repository:

.. code-block:: bash

   # List all available repositories
   dbx test --list

   # Run tests in a specific repository
   dbx test mongo-python-driver

   # Run tests matching a keyword expression
   dbx test mongo-python-driver --keyword "test_connection"

   # Short forms
   dbx test -l  # list
   dbx test mongo-python-driver -k "test_auth"  # filter tests

The ``test`` command will:

1. Find the repository by name across all cloned groups
2. Run ``pytest`` in the repository directory (with optional ``-k`` filter)
3. Display the test results

Example Output
--------------

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

Filter Tests by Keyword
-----------------------

The ``-k`` / ``--keyword`` flag passes a keyword expression to pytest's ``-k`` option to filter which tests to run. This is useful for:

- Running only tests matching a specific pattern (e.g., ``-k "test_connection"``)
- Running tests from a specific class (e.g., ``-k "TestAuth"``)
- Using boolean expressions (e.g., ``-k "test_auth and not test_slow"``)

The keyword expression is passed directly to pytest, so all pytest ``-k`` syntax is supported.

Requirements
------------

- The repository must be cloned first using ``dbx repo clone``
- The repository must have pytest installed
