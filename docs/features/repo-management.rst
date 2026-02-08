Repository Management
=====================

The ``dbx repo`` command provides repository management functionality for cloning and managing groups of related repositories.

Initialize Configuration
------------------------

Before using the repo commands, initialize your configuration file:

.. code-block:: bash

   # Create user configuration file at ~/.config/dbx-python-cli/config.toml
   dbx init

This creates a configuration file with default repository groups that you can customize.

Clone Repositories by Group
----------------------------

Clone repositories from predefined groups:

.. code-block:: bash

   # Clone pymongo repositories
   dbx repo clone -g pymongo

   # Clone langchain repositories
   dbx repo clone -g langchain

   # Clone django repositories
   dbx repo clone -g django

   # List available groups
   dbx repo clone -l

Fork-Based Workflow
~~~~~~~~~~~~~~~~~~~

For contributing to upstream repositories, you can clone from your personal fork and automatically set up the upstream remote:

.. code-block:: bash

   # Clone from your GitHub fork instead of the upstream org
   dbx repo clone -g pymongo --fork aclark4life

This will:

1. Clone from ``git@github.com:aclark4life/mongo-python-driver.git`` (your fork)
2. Add an ``upstream`` remote pointing to ``git@github.com:mongodb/mongo-python-driver.git`` (original repo)
3. Set up your local repository ready for the fork-based contribution workflow

**Example workflow:**

.. code-block:: bash

   # Clone your forks with upstream remotes configured
   dbx repo clone -g pymongo --fork aclark4life

   # Now you can work with the standard fork workflow
   cd ~/Developer/mongodb/pymongo/mongo-python-driver
   git remote -v
   # origin    git@github.com:aclark4life/mongo-python-driver.git (fetch)
   # origin    git@github.com:aclark4life/mongo-python-driver.git (push)
   # upstream  git@github.com:mongodb/mongo-python-driver.git (fetch)
   # upstream  git@github.com:mongodb/mongo-python-driver.git (push)

   # Fetch latest changes from upstream
   git fetch upstream
   git merge upstream/main

**Configuration:**

You can set a default fork username in your configuration file to avoid typing it every time:

.. code-block:: toml

   [repo]
   base_dir = "~/Developer/mongodb"
   fork_user = "aclark4life"  # Your GitHub username

   [repo.groups.pymongo]
   repos = [
       "git@github.com:mongodb/mongo-python-driver.git",
   ]

With this configuration, you can simply run:

.. code-block:: bash

   # Uses fork_user from config
   dbx repo clone -g pymongo --fork

   # Or override the config
   dbx repo clone -g pymongo --fork different-user

Sync Fork with Upstream
~~~~~~~~~~~~~~~~~~~~~~~~

After cloning with the fork workflow, you can easily sync your local repository with upstream changes:

.. code-block:: bash

   # Sync a specific repository
   dbx repo sync mongo-python-driver

   # Sync all repositories in a group
   dbx repo sync -g pymongo

   # Force push after rebasing (use if previous sync failed to push)
   dbx repo sync mongo-python-driver --force

   # List available repositories
   dbx repo sync -l

This command will:

1. Fetch the latest changes from the ``upstream`` remote
2. Rebase your current branch on top of ``upstream/<current-branch>``
3. Push the rebased branch to ``origin`` (your fork)
4. If ``--force`` is used, force push with ``--force-with-lease`` for safety

**Example workflow:**

.. code-block:: bash

   # Clone your fork with upstream configured
   dbx repo clone -g pymongo --fork aclark4life

   # Make some changes in your fork
   cd ~/Developer/mongodb/pymongo/mongo-python-driver
   git checkout -b my-feature
   # ... make changes ...
   git commit -am "Add new feature"

   # Sync with upstream to get latest changes and push
   dbx repo sync mongo-python-driver
   # Fetches from upstream, rebases your branch, and pushes to origin

   # Your changes are now in your fork, ready for a pull request!

**Notes:**

- The ``sync`` command requires an ``upstream`` remote to be configured
- If you cloned with ``--fork``, the upstream remote is automatically set up
- The command will rebase your current branch on ``upstream/<current-branch>``
- After rebasing, it automatically pushes to ``origin/<current-branch>``
- If the push fails (e.g., you've already pushed and rebased), use ``--force`` flag
- The ``--force`` flag uses ``--force-with-lease`` for safety (won't overwrite others' changes)
- If there are rebase conflicts, you'll need to resolve them manually
- Works with any repository that has an ``upstream`` remote, not just forks

**Available Groups (Default):**

- ``pymongo`` - MongoDB Python driver repositories (PyMongo, Specifications)
- ``langchain`` - LangChain framework repositories
- ``django`` - Django web framework repositories (Django, django-mongodb-backend)

**Configuration:**

Repository groups are defined in ``~/.config/dbx-python-cli/config.toml``. The default base directory for cloning is ``~/Developer/dbx-repos``, which can be customized.

Repositories are cloned into subdirectories named after their group. For example, the ``pymongo`` group will be cloned to ``~/Developer/dbx-repos/pymongo/``.

.. code-block:: toml

   [repo]
   base_dir = "~/Developer/dbx-repos"

   [repo.groups.pymongo]
   repos = [
       "https://github.com/mongodb/mongo-python-driver.git",
       "https://github.com/mongodb/specifications.git",
   ]

   [repo.groups.django]
   repos = [
       "https://github.com/django/django.git",
       "https://github.com/mongodb-labs/django-mongodb-backend.git",
   ]

   [repo.groups.custom]
   repos = [
       "https://github.com/your-org/your-repo.git",
   ]

You can add your own custom groups by editing the configuration file.

**Features:**

- User-specific configuration file (works with pip-installed package)
- Clones all repositories in a group to the configured base directory
- Skips repositories that already exist locally
- Fork-based workflow support with automatic upstream remote configuration
- Sync command to fetch from upstream and rebase current branch
- Provides clear progress feedback with emoji indicators
- Handles errors gracefully and continues with remaining repositories
- Easy to add custom repository groups
