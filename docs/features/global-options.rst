Global Options
==============

Verbose Mode
------------

Use the ``-v`` / ``--verbose`` flag to see more detailed output from any command:

.. code-block:: bash

   # Show verbose output when installing dependencies
   dbx -v install mongo-python-driver -e test

   # Show verbose output when running tests
   dbx -v test mongo-python-driver

   # Show verbose output when cloning repositories
   dbx -v repo clone -g pymongo

   # Show verbose output when running just commands
   dbx -v just mongo-python-driver lint

**What verbose mode shows:**

- Configuration details (base directory, config values)
- Full command being executed
- Working directory for subprocess commands
- Additional diagnostic information

**Note:** The verbose flag must come **before** the subcommand (e.g., ``dbx -v test``, not ``dbx test -v``).
