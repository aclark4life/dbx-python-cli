Git Operations
==============

**Decision: Use subprocess with git CLI instead of GitPython**

We chose to use Python's ``subprocess`` module to call the ``git`` command-line tool directly rather than using the GitPython library. This differs from `django-mongodb-cli <https://github.com/mongodb-labs/django-mongodb-cli>`_, which uses GitPython for its git operations. We evaluated both approaches and chose subprocess for the reasons outlined below.

Rationale
---------

1. **Simplicity** - Using subprocess with git CLI is straightforward and requires no additional dependencies beyond git itself, which developers already have installed.

2. **Reliability** - The git CLI is the canonical implementation and is guaranteed to work correctly. We avoid potential bugs or limitations in third-party libraries.

3. **Minimal Dependencies** - By not adding GitPython as a dependency, we keep the package lightweight and reduce potential dependency conflicts.

4. **Transparency** - Subprocess calls make it clear exactly what git commands are being executed, making debugging easier.

5. **Performance** - For simple clone operations, the overhead of spawning a subprocess is negligible, and we avoid loading a large library.

6. **Industry Standard** - This approach mirrors how IDEs and other development tools integrate git. Tools like VS Code, IntelliJ IDEA, and PyCharm all invoke the git CLI rather than reimplementing git operations. This proven pattern provides a reliable foundation for repository management.

Trade-offs
----------

- We need to handle subprocess errors and parse output manually
- Less Pythonic than using a native Python library
- Requires git to be installed on the system

Implementation
--------------

.. code-block:: python

   subprocess.run(
       ["git", "clone", repo_url, str(repo_path)],
       check=True,
       capture_output=True,
       text=True,
   )

This approach aligns with our philosophy of keeping the tool simple, transparent, and focused on developer workflows.
