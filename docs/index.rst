dbx-python-cli Documentation
============================

A command line tool for DBX Python development tasks. AI first. De-siloing happens here. Inspired by `django-mongodb-cli <https://github.com/mongodb-labs/django-mongodb-cli>`_.

About
-----

DBX Python is the MongoDB Database Experience Team for the MongoDB Python driver.

.. note::
   This is not `Databricks for Python developers <https://docs.databricks.com/aws/en/languages/python>`__.

.. raw:: html

   <script>
   document.addEventListener('DOMContentLoaded', function() {
       var links = document.querySelectorAll('a[href="https://docs.databricks.com/aws/en/languages/python"]');
       links.forEach(function(link) {
           link.setAttribute('target', '_blank');
           link.setAttribute('rel', 'noopener noreferrer');
       });
   });
   </script>

Feature Highlights
------------------

- 🤖 **AI-First Design** - Built with AI-assisted development workflows in mind
- 🔧 **Modern Tooling** - Uses the latest Python development tools and best practices
- 📦 **Fast Package Management** - Powered by `uv <https://github.com/astral-sh/uv>`_
- ✨ **Quality Focused** - Pre-commit hooks with `prek <https://github.com/aclark4life/prek>`_ and `ruff <https://github.com/astral-sh/ruff>`_
- 📚 **Well Documented** - Sphinx documentation with the beautiful Furo theme
- ✅ **Fully Tested** - Comprehensive test suite with pytest and coverage reporting

See :doc:`features/index` for detailed feature documentation.

Installation
------------

Via uv tool (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install directly from GitHub
   uv tool install git+https://github.com/aclark4life/dbx-python-cli.git

This will install ``dbx-python-cli`` globally and make the ``dbx`` command available in your terminal.

Quick Start
-----------

.. code-block:: bash

   # Initialize configuration
   dbx init

   # Clone repositories by group
   dbx repo clone -g pymongo

Contributing
------------

Interested in contributing? See the :doc:`development/index` section for detailed information on:

- Setting up your development environment
- Running tests
- Building documentation
- Contributing guidelines

Documentation
-------------

.. toctree::
   :maxdepth: 2

   features/index
   design/index
   api/index
   development/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
