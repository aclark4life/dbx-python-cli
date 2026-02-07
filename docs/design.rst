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

**Status: Design in progress - implementation details TBD**

Current State
~~~~~~~~~~~~~

**dbx-python-cli Installation**

``dbx-python-cli`` is expected to be installed via pipx:

.. code-block:: bash

   pipx install dbx-python-cli

This keeps the ``dbx`` command available globally, isolated from project dependencies.

**Repository Management**

Users can configure a base directory and clone repository groups:

.. code-block:: bash

   # Configure base directory (e.g., ~/Developer/mongodb)
   # Edit ~/.config/dbx-python-cli/config.toml

   # Clone repository groups
   dbx repo clone -g pymongo

This creates a structure like:

.. code-block:: text

   ~/Developer/mongodb/
   ├── pymongo/
   │   ├── mongo-python-driver/
   │   ├── specifications/
   │   └── drivers-evergreen-tools/

Future Work
~~~~~~~~~~~

**Virtual Environment Management**

``dbx`` will manage virtual environments for cloned repositories in ways TBD.

Considerations include:

- How to create/detect/use venvs for repositories
- Whether to auto-create venvs or require explicit commands
- How commands (``dbx test``, ``dbx install``, etc.) interact with venvs
- Whether to support multiple venv strategies (per-repo, per-group, workspace-level)

**Technical Note: Running Commands in Venvs**

When ``dbx`` (running in pipx's isolated environment) needs to execute commands in a repository's venv, it cannot use ``source`` or activation scripts in subprocesses. Instead, it must directly invoke the venv's Python executable:

.. code-block:: python

   # ❌ WRONG - Activation doesn't work in subprocess
   subprocess.run("source .venv/bin/activate && pytest", shell=True)

   # ✅ CORRECT - Directly invoke venv's Python
   subprocess.run([".venv/bin/python", "-m", "pytest"], cwd=repo_path)

This is because:

1. Activation scripts modify the current shell's environment
2. Subprocess environments don't persist across commands
3. The venv's Python executable knows where its packages are without activation
