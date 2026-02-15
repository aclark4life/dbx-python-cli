Command Structure
=================

This document explains the design decision to use top-level commands instead of nested command groups.

Decision
--------

We prefer **top-level commands** (``dbx clone``, ``dbx sync``) over **nested command groups** (``dbx repo clone``, ``dbx repo sync``).

Rationale
---------

Simplicity and Discoverability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Top-level commands are more discoverable and easier to use:

- **Shorter commands**: ``dbx clone -g pymongo`` vs ``dbx repo clone -g pymongo``
- **Fewer concepts**: Users don't need to understand command groups
- **Better help output**: Commands appear directly in ``dbx --help``

Common Usage Patterns
~~~~~~~~~~~~~~~~~~~~~

The most frequently used commands should be at the top level:

- ``dbx clone`` - Clone repositories from a group
- ``dbx sync`` - Sync repositories with upstream
- ``dbx install`` - Install packages
- ``dbx test`` - Run tests

These are the primary workflows, so they should be as accessible as possible.

Consistency with Git
~~~~~~~~~~~~~~~~~~~~

Git uses top-level commands (``git clone``, ``git pull``, ``git push``) rather than nested groups (``git repo clone``). This pattern is familiar to developers.

When to Use Command Groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Command groups are still useful for:

- **Related subcommands**: ``dbx env create``, ``dbx env activate``, ``dbx env list``
- **Namespacing**: When multiple commands share a common domain (e.g., environment management)
- **Organization**: When there are many related commands that would clutter the top level

Examples
--------

Top-Level Commands (Preferred)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clone repositories
   dbx clone -g pymongo

   # Sync a repository
   dbx sync mongo-python-driver

   # List repositories
   dbx -l

Command Groups (When Appropriate)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Environment management
   dbx env create -g pymongo
   dbx env activate -g pymongo
   dbx env list

   # Project management
   dbx project add myproject
   dbx project run myproject
   dbx project -l

Migration Notes
---------------

This decision was implemented in a refactoring that moved ``clone`` and ``sync`` from the ``repo`` command group to the top level.

**Before:**

.. code-block:: bash

   dbx repo clone -g pymongo
   dbx repo sync mongo-python-driver
   dbx repo -l

**After:**

.. code-block:: bash

   dbx clone -g pymongo
   dbx sync mongo-python-driver
   dbx -l

The ``repo.py`` module was converted from a command module to a helper functions module, containing only utility functions like ``get_config()``, ``get_base_dir()``, and ``get_repo_groups()``.

Smart Defaults for Convenience
-------------------------------

To further improve usability, commands should provide smart defaults when possible. This reduces typing and makes common workflows faster.

Project Commands Default to Newest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most ``dbx project`` commands default to the newest project when no project name is specified:

.. code-block:: bash

   # These commands work without specifying a project name
   dbx project run              # Run newest project
   dbx project manage shell     # Open shell on newest project
   dbx project su               # Create superuser on newest project
   dbx project migrate          # Run migrations on newest project
   dbx project remove           # Remove newest project

The "newest" project is determined by filesystem modification time. This is particularly useful during active development when you're frequently working with the same project.

When a command defaults to the newest project, it displays an informative message:

.. code-block:: text

   ℹ️  No project specified, using newest: 'myproject'

This design decision follows the principle of **optimizing for the common case**: developers typically work on one project at a time, so requiring the project name for every command adds unnecessary friction.

Future Considerations
---------------------

As the CLI grows, we should continue to evaluate whether commands belong at the top level or in a group:

- **Top level**: Frequently used, standalone operations
- **Command groups**: Related operations that share context or configuration

We should also look for opportunities to add smart defaults that reduce typing while maintaining clarity:

- **Sensible defaults**: Commands should work with minimal arguments for common use cases
- **Clear feedback**: When defaults are applied, inform the user what was chosen
- **Easy override**: Defaults should be easy to override when needed

The goal is to keep the CLI intuitive and easy to use while maintaining good organization.
