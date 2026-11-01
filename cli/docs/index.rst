multigit CLI documentation
==========================

This directory contains the documentation for the independently packaged
``multigit`` CLI distribution.

This package is built and tested as a standalone CLI component. The library
boundary remains the separate ``multigit-lib`` distribution, while the root
legacy package is retained only as compatibility coverage during the migration.

Command entry point
-------------------

.. autofunction:: multigit_cli.__main__.main

Subrepos file loading
---------------------

.. automodule:: multigit_cli.subrepofile
   :members:
   :undoc-members:

Recursive CLI workflow
----------------------

.. automodule:: multigit_cli.subrepos_orchestration
   :members:
   :undoc-members:

Command modes
-------------

The options are mutually exclusive. ``--help`` displays usage, ``--version``
prints the installed CLI version, ``--status`` reports repository states, and
``--run`` updates the repositories described by ``subrepos`` files.

.. code-block:: console

   multigit --help
   multigit --version
   multigit --status
   multigit --run

.. toctree::
   :maxdepth: 1
   :caption: Contents:

