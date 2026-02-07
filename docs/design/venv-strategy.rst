Virtual Environment Strategy
============================

**Decision: One virtual environment per group**

dbx-python-cli Installation
----------------------------

``dbx-python-cli`` is expected to be installed via uv tool:

.. code-block:: bash

   uv tool install dbx-python-cli

This keeps the ``dbx`` command available globally, isolated from project dependencies.

Repository and Virtual Environment Structure
---------------------------------------------

Users configure a base directory and clone repository groups. Virtual environments are created at the group level:

.. code-block:: bash

   # Clone repository groups
   dbx repo clone -g pymongo

   # Create venv for the group
   dbx env init -g pymongo

This creates a structure like:

.. code-block:: text

   ~/Developer/mongodb/
   ├── pymongo/
   │   ├── .venv/                      # Group-level venv
   │   ├── mongo-python-driver/
   │   ├── specifications/
   │   └── drivers-evergreen-tools/
   ├── langchain/
   │   ├── .venv/                      # Separate group venv
   │   └── langchain/

Rationale
---------

- **Group-level venvs** - Repos in the same group (e.g., pymongo repos) typically share dependencies
- **Simpler management** - One venv per group instead of many per-repo venvs
- **Disk efficient** - Fewer duplicate dependencies

Command Behavior
----------------

dbx env init
~~~~~~~~~~~~

Create a virtual environment for a group:

.. code-block:: bash

   # Create venv for pymongo group
   dbx env init -g pymongo

   # Create with specific Python version
   dbx env init -g pymongo --python 3.11

dbx install
~~~~~~~~~~~

Install dependencies, using group venv if available:

.. code-block:: bash

   # Uses pymongo group venv if it exists
   dbx install mongo-python-driver -e test

   # Falls back to system Python if no venv found

dbx test
~~~~~~~~

Run tests, using group venv if available:

.. code-block:: bash

   # Uses pymongo group venv if it exists
   dbx test mongo-python-driver

   # Falls back to system Python if no venv found

Venv Detection
--------------

Commands detect and use venvs in this order:

1. **Group-level venv** - ``<group_path>/.venv``
2. **System Python** - Fallback if no venv found

Technical Implementation
------------------------

Running Commands in Venvs
~~~~~~~~~~~~~~~~~~~~~~~~~~

When ``dbx`` (running in uvx's isolated environment) needs to execute commands in a venv, it cannot use ``source`` or activation scripts in subprocesses. Instead, it must directly invoke the venv's Python executable:

.. code-block:: python

   # ❌ WRONG - Activation doesn't work in subprocess
   subprocess.run("source .venv/bin/activate && pytest", shell=True)

   # ✅ CORRECT - Directly invoke venv's Python
   subprocess.run([".venv/bin/python", "-m", "pytest"], cwd=repo_path)

This is because:

1. Activation scripts modify the current shell's environment
2. Subprocess environments don't persist across commands
3. The venv's Python executable knows where its packages are without activation

Venv Detection Example
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def get_venv_python(repo_path, group_path):
       """Get Python executable from group venv."""
       # Check group-level venv
       group_venv = group_path / ".venv" / "bin" / "python"
       if group_venv.exists():
           return str(group_venv)

       # Fallback to system Python
       return "python"
