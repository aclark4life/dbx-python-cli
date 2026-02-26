Installation
============

This guide covers installing dbx-python-cli on your system.

Prerequisites
-------------

Before installing dbx-python-cli, you'll need:

- **Python 3.11 or higher**
- **pipx** - Install Python applications in isolated environments

Installing pipx
~~~~~~~~~~~~~~~

If you don't have pipx installed, install it first:

**macOS:**

.. code-block:: bash

   brew install pipx
   pipx ensurepath

**Linux:**

.. code-block:: bash

   pip install pipx
   pipx ensurepath

**Windows:**

.. code-block:: bash

   pip install pipx
   pipx ensurepath

For more installation options, see the `pipx documentation <https://pipx.pypa.io/>`_.

Installing dbx-python-cli
--------------------------

Via pipx (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~

The recommended way to install dbx-python-cli is using ``pipx install``:

.. code-block:: bash

   # Install directly from GitHub
   pipx install git+https://github.com/aclark4life/dbx-python-cli.git

This will:

- Install dbx-python-cli in an isolated environment
- Make the ``dbx`` command available globally in your terminal
- Keep the tool separate from your project dependencies

Verify Installation
~~~~~~~~~~~~~~~~~~~

After installation, verify that the ``dbx`` command is available:

.. code-block:: bash

   dbx --help

You should see the help message with available commands.

Updating
--------

To update dbx-python-cli to the latest version:

.. code-block:: bash

   pipx upgrade dbx-python-cli

Or to reinstall a specific version:

.. code-block:: bash

   pipx install --force git+https://github.com/aclark4life/dbx-python-cli.git@<version>

Uninstalling
------------

To uninstall dbx-python-cli:

.. code-block:: bash

   pipx uninstall dbx-python-cli

Next Steps
----------

After installation, proceed to the :doc:`quick-start` guide to set up your first project.
