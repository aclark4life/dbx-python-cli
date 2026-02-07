Design Decisions
================

This page documents key design decisions made in the development of dbx-python-cli.

Git Operations
--------------

**Decision: Use subprocess with git CLI instead of GitPython**

We chose to use Python's ``subprocess`` module to call the ``git`` command-line tool directly rather than using the GitPython library.

**Rationale:**

1. **Simplicity** - Using subprocess with git CLI is straightforward and requires no additional dependencies beyond git itself, which developers already have installed.

2. **Reliability** - The git CLI is the canonical implementation and is guaranteed to work correctly. We avoid potential bugs or limitations in third-party libraries.

3. **Minimal Dependencies** - By not adding GitPython as a dependency, we keep the package lightweight and reduce potential dependency conflicts.

4. **Transparency** - Subprocess calls make it clear exactly what git commands are being executed, making debugging easier.

5. **Performance** - For simple clone operations, the overhead of spawning a subprocess is negligible, and we avoid loading a large library.

**Trade-offs:**

- We need to handle subprocess errors and parse output manually
- Less Pythonic than using a native Python library
- Requires git to be installed on the system

**Implementation:**

.. code-block:: python

   subprocess.run(
       ["git", "clone", repo_url, str(repo_path)],
       check=True,
       capture_output=True,
       text=True,
   )

This approach aligns with our philosophy of keeping the tool simple, transparent, and focused on developer workflows.

Virtual Environment Strategy
-----------------------------

**Decision: One virtual environment per group, with optional per-repo venvs**

dbx-python-cli Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``dbx-python-cli`` is expected to be installed via uvx:

.. code-block:: bash

   uvx --from dbx-python-cli dbx

Or install it persistently:

.. code-block:: bash

   uv tool install dbx-python-cli

This keeps the ``dbx`` command available globally, isolated from project dependencies.

Repository and Virtual Environment Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

**Rationale:**

- **Group-level venvs** - Repos in the same group (e.g., pymongo repos) typically share dependencies
- **Simpler management** - One venv per group instead of many per-repo venvs
- **Flexibility** - Repos can still have their own ``.venv`` if needed (detected and used automatically)
- **Disk efficient** - Fewer duplicate dependencies

Command Behavior
~~~~~~~~~~~~~~~~

**dbx env init**

Create a virtual environment for a group:

.. code-block:: bash

   # Create venv for pymongo group
   dbx env init -g pymongo

   # Create with specific Python version
   dbx env init -g pymongo --python 3.11

**dbx install**

Install dependencies, using group venv or repo venv if available:

.. code-block:: bash

   # Uses pymongo group venv if it exists
   dbx install mongo-python-driver -e test

   # If repo has its own .venv, uses that instead
   # Falls back to system Python if no venv found

**dbx test**

Run tests, using group venv or repo venv if available:

.. code-block:: bash

   # Uses pymongo group venv if it exists
   dbx test mongo-python-driver

   # If repo has its own .venv, uses that instead
   # Falls back to system Python if no venv found

Venv Detection Priority
~~~~~~~~~~~~~~~~~~~~~~~~

Commands detect and use venvs in this order:

1. **Repo-level venv** - ``<repo_path>/.venv`` (highest priority)
2. **Group-level venv** - ``<group_path>/.venv``
3. **System Python** - Fallback if no venv found

This allows flexibility: most repos use the group venv, but individual repos can opt for their own venv if needed.

Technical Implementation
~~~~~~~~~~~~~~~~~~~~~~~~

**Running Commands in Venvs**

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

**Venv Detection Example**

.. code-block:: python

   def get_venv_python(repo_path, group_path):
       """Get Python executable, checking repo then group venv."""
       # Check repo-level venv first
       repo_venv = repo_path / ".venv" / "bin" / "python"
       if repo_venv.exists():
           return str(repo_venv)

       # Check group-level venv
       group_venv = group_path / ".venv" / "bin" / "python"
       if group_venv.exists():
           return str(group_venv)

       # Fallback to system Python
       return "python"
