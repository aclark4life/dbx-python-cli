Installation
============

This guide covers installing dbx-python-cli on your system.

Prerequisites
-------------

Before installing dbx-python-cli, you'll need:

- **Python 3.10 or higher**
- **uv** - Ultra-fast Python package installer and tool manager

Installing uv
~~~~~~~~~~~~~

If you don't have uv installed, install it first:

**macOS/Linux:**

.. code-block:: bash

   curl -LsSf https://astral.sh/uv/install.sh | sh

**Windows:**

.. code-block:: powershell

   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

For more installation options, see the `uv documentation <https://github.com/astral-sh/uv>`_.

Installing dbx-python-cli
--------------------------

Via uv tool (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~

The recommended way to install dbx-python-cli is using ``uv tool install``:

.. code-block:: bash

   # Install directly from GitHub
   uv tool install git+https://github.com/aclark4life/dbx-python-cli.git

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

   uv tool upgrade dbx-python-cli

Or to install a specific version:

.. code-block:: bash

   uv tool install --force git+https://github.com/aclark4life/dbx-python-cli.git@<version>

Uninstalling
------------

To uninstall dbx-python-cli:

.. code-block:: bash

   uv tool uninstall dbx-python-cli

Optional Dependencies
---------------------

While not required for dbx-python-cli itself, you may want to install these tools for enhanced functionality:

just (Command Runner)
~~~~~~~~~~~~~~~~~~~~~

`just <https://github.com/casey/just>`_ is a command runner that many repositories use for task automation:

**macOS:**

.. code-block:: bash

   brew install just

**Linux:**

.. code-block:: bash

   cargo install just

**Windows:**

.. code-block:: bash

   cargo install just

Or download from the `just releases page <https://github.com/casey/just/releases>`_.

Git
~~~

Git is required for cloning and managing repositories:

**macOS:**

.. code-block:: bash

   brew install git

**Linux:**

.. code-block:: bash

   sudo apt-get install git  # Debian/Ubuntu
   sudo yum install git      # RHEL/CentOS

**Windows:**

Download from `git-scm.com <https://git-scm.com/download/win>`_.

Next Steps
----------

After installation, proceed to the :doc:`quick-start` guide to set up your first project.
