Project Management
==================

The ``dbx project`` command provides tools for creating and managing Django projects with MongoDB backend support.

Overview
--------

Projects are Django applications created from bundled templates that include:

- Django project structure with MongoDB backend configuration
- Optional frontend application with webpack setup
- Pre-configured settings for different environments (base, qe, etc.)
- Justfile for common development tasks
- Pre-generated migrations for Django's built-in apps

Projects are created in ``base_dir/projects/`` by default, where ``base_dir`` is configured in your ``~/.config/dbx-python-cli/config.toml`` file.

Creating Projects
-----------------

Create a new Django project with the ``add`` command:

.. code-block:: bash

   # Create a project with explicit name (includes frontend by default)
   dbx project add myproject

   # Create without frontend
   dbx project add myproject --no-frontend

   # Generate a random project name
   dbx project add --random

   # Use specific settings configuration
   dbx project add myproject --settings=qe

   # Create in a custom directory
   dbx project add myproject -d ~/custom/path

The ``--random`` flag generates a creative project name using random adjectives and nouns (e.g., "cosmic_nebula", "quantum_forest").

Project Structure
-----------------

A generated project includes:

.. code-block:: text

   myproject/
   ├── manage.py
   ├── pyproject.toml
   ├── justfile
   ├── myproject/
   │   ├── __init__.py
   │   ├── settings/
   │   │   ├── __init__.py
   │   │   ├── base.py
   │   │   ├── qe.py
   │   │   └── myproject.py
   │   ├── urls.py
   │   ├── wsgi.py
   │   └── migrations/
   └── frontend/  (if --add-frontend)
       ├── package.json
       ├── webpack/
       └── src/

Installing Projects
-------------------

Projects can be installed using the standard ``dbx install`` command:

.. code-block:: bash

   # Install a project (automatically finds it in base_dir/projects/)
   dbx install myproject

This will:

1. Install the project's Python dependencies using pip
2. Install frontend npm dependencies if a frontend exists

Removing Projects
-----------------

Remove a project with the ``remove`` command:

.. code-block:: bash

   # Remove a project
   dbx project remove myproject

   # Remove from custom directory
   dbx project remove myproject -d ~/custom/path

This will:

1. Attempt to uninstall the project package from the current Python environment
2. Remove the project directory from the filesystem

Virtual Environments
--------------------

Projects use a shared virtual environment in the ``projects/`` directory:

.. code-block:: bash

   # Create a virtual environment for all projects
   dbx env init -g projects

   # List all virtual environments
   dbx env list

**Current Limitation**: The virtual environment is created at the ``projects/`` level, not per individual project. This means all projects in the ``projects/`` directory share the same virtual environment.

.. note::

   **Future Enhancement**: Per-project virtual environments (e.g., ``projects/myproject/.venv``) may be added in a future release. For now, if you need isolated environments for different projects, you can use the ``--directory`` flag to create projects in separate locations and manage their virtual environments independently.

Configuration
-------------

Projects are created in the directory specified by ``base_dir`` in your configuration file:

.. code-block:: toml

   [repo]
   base_dir = "~/Developer/mongodb"

With this configuration, projects will be created in ``~/Developer/mongodb/projects/``.

Settings Configurations
-----------------------

Projects support multiple settings configurations:

- ``base``: Default settings (used if no ``--settings`` flag is provided)
- ``qe``: QE environment settings
- ``<project_name>``: Project-specific settings

You can specify which settings to use when creating a project:

.. code-block:: bash

   dbx project add myproject --settings=qe

This sets the ``DJANGO_SETTINGS_MODULE`` in the generated ``pyproject.toml`` to use the specified settings module.

