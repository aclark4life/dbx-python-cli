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

**Decision: One virtual environment per repository, with dbx-python-cli installed globally via pipx**

We recommend a clear separation between the dbx-python-cli tool itself and the repositories it manages.

Problem Statement
~~~~~~~~~~~~~~~~~

Users need a clear strategy for managing virtual environments when:

1. Installing and using ``dbx-python-cli`` itself
2. Developing on cloned repositories (pymongo, django, etc.)

Recommended Strategy
~~~~~~~~~~~~~~~~~~~~

**For dbx-python-cli Installation**

Install with pipx (recommended):

.. code-block:: bash

   pipx install dbx-python-cli

**Why pipx?**

- Keeps ``dbx`` command available globally
- Isolated from project dependencies
- No venv activation needed
- Standard practice for CLI tools

**Alternative: System-wide pip install**

.. code-block:: bash

   pip install --user dbx-python-cli

**For Target Repositories**

**Strategy: One venv per repository**

Each cloned repository should have its own virtual environment:

.. code-block:: text

   ~/Developer/mongodb/
   ├── pymongo/
   │   ├── mongo-python-driver/
   │   │   ├── .venv/              # Dedicated venv
   │   │   ├── pyproject.toml
   │   │   └── ...
   │   ├── specifications/
   │   │   ├── .venv/              # Separate venv
   │   │   └── ...
   │   └── drivers-evergreen-tools/
   │       ├── .venv/              # Separate venv
   │       └── ...

**Why one venv per repo?**

- ✅ Dependency isolation (different versions, different Python versions)
- ✅ Matches standard development workflow
- ✅ Prevents version conflicts
- ✅ Each repo can be tested independently
- ✅ Easier to clean up (just delete .venv)

**Why NOT one venv per group?**

- ❌ Dependency conflicts between repos in same group
- ❌ Different repos may need different Python versions
- ❌ Harder to isolate issues
- ❌ Not standard practice

Proposed Features
~~~~~~~~~~~~~~~~~

**1. Venv Creation Command**

Add ``dbx venv`` command:

.. code-block:: bash

   # Create venv for a repository
   dbx venv create mongo-python-driver

   # Create with specific Python version
   dbx venv create mongo-python-driver --python 3.11

   # List venvs
   dbx venv list

   # Remove venv
   dbx venv remove mongo-python-driver

**2. Auto-create During Install**

Add ``--create-venv`` flag to ``dbx install``:

.. code-block:: bash

   # Create venv and install dependencies
   dbx install mongo-python-driver --create-venv -e test

   # Or make it the default behavior with opt-out
   dbx install mongo-python-driver -e test  # Creates venv if missing
   dbx install mongo-python-driver -e test --no-venv  # Skip venv creation

**3. Venv Activation Helper**

Since we can't activate a venv from a subprocess, provide helper:

.. code-block:: bash

   # Print activation command
   dbx venv activate mongo-python-driver
   # Output: source ~/Developer/mongodb/pymongo/mongo-python-driver/.venv/bin/activate

   # Use with eval for convenience
   eval "$(dbx venv activate mongo-python-driver)"

**4. Venv-aware Commands**

Commands should detect and use existing venvs:

.. code-block:: bash

   # If .venv exists, use it automatically
   dbx test mongo-python-driver
   dbx just mongo-python-driver lint
   dbx install mongo-python-driver -e test

Implementation Details
~~~~~~~~~~~~~~~~~~~~~~

**Venv Detection**

.. code-block:: python

   def get_venv_path(repo_path):
       """Get the venv path for a repository."""
       venv_path = repo_path / ".venv"
       if venv_path.exists():
           return venv_path
       return None

   def get_venv_python(repo_path):
       """Get the Python executable from the venv."""
       venv_path = get_venv_path(repo_path)
       if venv_path:
           return venv_path / "bin" / "python"
       return "python"  # Fallback to system Python

**Venv Creation with uv**

.. code-block:: python

   def create_venv(repo_path, python_version=None):
       """Create a virtual environment using uv."""
       cmd = ["uv", "venv"]
       if python_version:
           cmd.extend(["--python", python_version])

       subprocess.run(cmd, cwd=repo_path, check=True)

Testing Strategy
~~~~~~~~~~~~~~~~

**Unit Tests**

- Test venv detection logic
- Test venv creation with different Python versions
- Test venv-aware command execution

**Integration Tests**

- Test full workflow: clone → create venv → install → test
- Test with and without venvs
- Test venv reuse (don't recreate if exists)

**Manual Testing Scenarios**

1. Fresh install: ``pipx install dbx-python-cli``
2. Clone repos: ``dbx repo clone -g pymongo``
3. Create venv: ``dbx venv create mongo-python-driver``
4. Install deps: ``dbx install mongo-python-driver -e test``
5. Run tests: ``dbx test mongo-python-driver``

Documentation Updates
~~~~~~~~~~~~~~~~~~~~~

- Add "Virtual Environment Guide" to docs
- Update installation docs to recommend pipx
- Add venv examples to all command docs
- Create troubleshooting guide for venv issues

Migration Path
~~~~~~~~~~~~~~

For existing users:

1. Document the recommended approach
2. Make venv creation opt-in initially
3. Add warnings if no venv detected
4. Consider making it default in v1.0

Open Questions
~~~~~~~~~~~~~~

1. Should we default to creating venvs or require explicit flag?
2. Should we support other venv tools (virtualenv, venv)?
3. Should we integrate with direnv for auto-activation?
4. Should we support workspace-level venvs (one venv for all repos)?

**Rationale:**

This strategy provides clear separation of concerns:

- **dbx-python-cli** is a tool, installed globally and always available
- **Target repositories** are development projects, each with isolated dependencies
- **uv** provides fast, modern venv and package management
- **Standard practices** align with how Python developers typically work

**Trade-offs:**

- Multiple venvs use more disk space (but disk is cheap)
- Users need to activate the correct venv for each repo (but this is standard practice)
- More complex than a single shared venv (but much more robust)

**Implementation Priority:**

1. **Phase 1** (Now): Document current best practices
2. **Phase 2** (Next): Add ``dbx venv create/list/activate`` commands
3. **Phase 3** (Later): Make commands venv-aware automatically
4. **Phase 4** (Future): Auto-create venvs during install (opt-in → default)
