Features
========

This section provides detailed documentation for all dbx-python-cli features.

.. toctree::
   :hidden:

   global-options
   repo-management
   project-management
   installation
   testing
   just-commands

Global Options
--------------

The CLI supports global options that can be used with any command. See :doc:`global-options` for details.

Repository Management
---------------------

The ``dbx clone``, ``dbx sync``, and ``dbx branch`` commands provide repository management functionality for cloning, syncing, and viewing branches in groups of related repositories. See :doc:`repo-management` for details.

Project Management
------------------

The ``dbx project`` command provides tools for creating and managing Django projects with MongoDB backend support. See :doc:`project-management` for details.

Installation
------------

Install dependencies in any cloned repository using ``uv pip install``. See :doc:`installation` for details.

Testing
-------

Run pytest in any cloned repository. See :doc:`testing` for details.

Just Commands
-------------

Run `just <https://github.com/casey/just>`_ commands in any cloned repository. See :doc:`just-commands` for details.
