Project Management
==================

The ``dbx project`` command provides tools for creating and managing Django projects with MongoDB backend support.

Overview
--------

Projects are Django applications created from bundled templates that include:

- Django project structure with MongoDB backend configuration
- Optional frontend application with webpack setup
- Pre-configured settings with commented Queryable Encryption (QE) support
- Justfile for common development tasks
- Pre-generated migrations for Django's built-in apps

Projects are created in ``base_dir/projects/`` by default, where ``base_dir`` is configured in your ``~/.config/dbx-python-cli/config.toml`` file.

Newest Project Default
~~~~~~~~~~~~~~~~~~~~~~

**Most project commands default to the newest project when no project name is specified.** This makes it easier to work with your most recent project without having to type the project name repeatedly.

The "newest" project is determined by the most recently modified project directory (based on filesystem modification time). When a command defaults to the newest project, you'll see an informative message:

.. code-block:: text

   ℹ️  No project specified, using newest: 'myproject'

Commands that support this behavior:

- ``dbx project run`` - Run the Django development server
- ``dbx project remove`` - Remove a project
- ``dbx project manage`` - Run Django management commands
- ``dbx project su`` - Create a superuser
- ``dbx project migrate`` - Run Django migrations

This feature is particularly useful during active development when you're frequently working with the same project.

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
   │   │   └── myproject.py  (includes commented QE configuration)
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
2. Automatically detect and install frontend npm dependencies if a ``frontend/`` directory with ``package.json`` exists

The ``dbx install`` command now supports frontend installation for both projects and regular repositories. If a ``frontend/`` directory is detected with a ``package.json`` file, npm dependencies will be installed automatically after the Python package installation completes.

Running Projects
----------------

Run a Django project's development server with the ``run`` command:

.. code-block:: bash

   # Run the newest project (no name required)
   dbx project run

   # Run a specific project
   dbx project run myproject

   # Run with custom host and port
   dbx project run myproject --host 0.0.0.0 --port 8080

   # Run with custom MongoDB URI
   dbx project run myproject --mongodb-uri mongodb://localhost:27017

This will:

1. Start the Django development server using ``manage.py runserver``
2. Automatically start the frontend development server if a ``frontend/`` directory exists
3. Handle graceful shutdown of both servers on CTRL-C

Managing Projects
-----------------

Run Django management commands with the ``manage`` command:

.. code-block:: bash

   # Run shell on the newest project (no name required)
   dbx project manage shell

   # Run migrations on a specific project
   dbx project manage myproject migrate

   # Create migrations
   dbx project manage myproject makemigrations

   # Run with MongoDB URI
   dbx project manage myproject --mongodb-uri mongodb://localhost:27017 shell

Creating Superusers
-------------------

Create a Django superuser with the ``su`` command:

.. code-block:: bash

   # Create superuser on the newest project (no name required)
   dbx project su

   # Create superuser on a specific project
   dbx project su myproject

   # Create with custom credentials
   dbx project su myproject -u admin -p secretpass -e admin@example.com

   # Create with custom MongoDB URI
   dbx project su myproject --mongodb-uri mongodb://localhost:27017

The default username and password are both ``admin``. The email defaults to the ``PROJECT_EMAIL`` environment variable or ``admin@example.com`` if not set.

Running Migrations
------------------

Run Django migrations with the ``migrate`` command:

.. code-block:: bash

   # Run migrations on the newest project (no name required)
   dbx project migrate

   # Run migrations on a specific project
   dbx project migrate myproject

   # Run migrations with custom settings
   dbx project migrate myproject --settings base

   # Run migrations on a specific database
   dbx project migrate myproject --database encrypted

   # Run migrations with custom MongoDB URI
   dbx project migrate myproject --mongodb-uri mongodb://localhost:27017

This is a convenience command that wraps ``django-admin migrate`` with the same environment setup as other project commands.

Removing Projects
-----------------

Remove a project with the ``remove`` command:

.. code-block:: bash

   # Remove the newest project (no name required)
   dbx project remove

   # Remove a specific project
   dbx project remove myproject

   # Remove from custom directory
   dbx project remove myproject -d ~/custom/path

This will:

1. Attempt to uninstall the project package from the current Python environment
2. Remove the project directory from the filesystem

.. note::

   When using the ``--directory`` flag, you must specify the project name explicitly.

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

Environment Variables
---------------------

Project commands automatically set environment variables from your ``~/.config/dbx-python-cli/config.toml`` file. The default configuration includes:

.. code-block:: toml

   [project.default_env]
   MONGODB_URI = "mongodb://localhost:27017"
   # Set the path to your libmongocrypt build for Queryable Encryption support
   PYMONGOCRYPT_LIB = "~/Developer/mongodb/django/libmongocrypt/cmake-build/libmongocrypt.dylib"  # macOS
   # PYMONGOCRYPT_LIB = "~/Developer/mongodb/django/libmongocrypt/cmake-build/libmongocrypt.so"     # Linux
   # DYLD_LIBRARY_PATH = "~/Developer/mongodb/django/libmongocrypt/cmake-build"  # macOS (alternative)
   # LD_LIBRARY_PATH = "~/Developer/mongodb/django/libmongocrypt/cmake-build"    # Linux (alternative)
   CRYPT_SHARED_LIB_PATH = "~/Downloads/mongo_crypt_shared_v1-macos-arm64-enterprise-8.2.2/lib/mongo_crypt_v1.dylib"  # macOS
   # CRYPT_SHARED_LIB_PATH = "~/Downloads/mongo_crypt_shared_v1-linux-x86_64-enterprise-8.2.2/lib/mongo_crypt_v1.so"     # Linux

These environment variables are automatically used by the ``run``, ``manage``, ``migrate``, and ``su`` commands. You can override them using command-line flags:

.. code-block:: bash

   # Override MongoDB URI
   dbx project run myproject --mongodb-uri mongodb://custom-host:27017

   # Environment variables from config are used if not overridden
   dbx project migrate myproject

Settings Configurations
-----------------------

Projects include multiple settings files:

- ``base.py``: Shared base settings
- ``<project_name>.py``: Project-specific settings (default) with commented Queryable Encryption configuration

The default ``DJANGO_SETTINGS_MODULE`` in the generated ``pyproject.toml`` uses the project-specific settings module (``<project_name>.settings.<project_name>``).

Queryable Encryption Support
-----------------------------

Projects include commented configuration for MongoDB Queryable Encryption (QE) in the main settings file. To enable QE:

1. **Uncomment the QE database configuration** in ``<project_name>/settings/<project_name>.py``:

   .. code-block:: python

      DATABASES = {
          "default": {
              "ENGINE": "django_mongodb_backend",
              "NAME": "<project_name>",
              "CLIENT": {
                  "host": os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
                  "auto_encryption_opts": AutoEncryptionOpts(
                      key_vault_namespace="<project_name>_encrypted.__keyVault",
                      kms_providers={
                          "local": {
                              "key": b"..."  # 96-byte key included in template
                          },
                      },
                      crypt_shared_lib_path=os.getenv("CRYPT_SHARED_LIB_PATH"),
                      crypt_shared_lib_required=True,
                  )
              },
          },
          # Optional: separate database for encrypted data
          "encrypted": {
              "ENGINE": "django_mongodb_backend",
              "NAME": "<project_name>_encrypted",
              "CLIENT": {
                  "host": os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
              },
          },
      }

2. **Uncomment the medical_records app** (if using the QE demo):

   .. code-block:: python

      INSTALLED_APPS = (
          INSTALLED_APPS
          + [
              "medical_records",  # Uncomment for QE demo
          ]
      )

3. **Ensure environment variables are set** in your ``~/.config/dbx-python-cli/config.toml``:

   - ``PYMONGOCRYPT_LIB``: Path to the libmongocrypt shared library
   - ``CRYPT_SHARED_LIB_PATH``: Path to the MongoDB Automatic Encryption Shared Library
   - ``MONGODB_URI``: MongoDB connection string (defaults to ``mongodb://localhost:27017``)

4. **Build libmongocrypt** (if not already built):

   .. code-block:: bash

      # Install libmongocrypt (includes cmake build step)
      dbx install libmongocrypt

The ``dbx install`` command will automatically run the cmake build commands configured in ``config.toml`` to build the libmongocrypt C library.

.. note::

   **Queryable Encryption Requirements:**

   - MongoDB 7.0+ (replica set or sharded cluster)
   - libmongocrypt C library (built via ``dbx install libmongocrypt``)
   - MongoDB Automatic Encryption Shared Library (download from MongoDB)
   - pymongocrypt Python package (installed automatically with django-mongodb-backend)
