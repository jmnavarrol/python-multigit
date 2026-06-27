multigit-lib documentation
==========================

Minimal library PoC documentation.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api

Outcome and Known Gaps
======================

Validated in this PoC
---------------------

* The lib/ subtree can be packaged independently with hatchling.
* Offline unittest smoke checks run successfully for the transitional
   ``multigit_lib`` package.
* Sphinx documentation builds successfully from the component-local docs/
   tree.
* The built wheel installs without exposing a ``multigit`` shell command.
* The built library package coexists with the current production ``multigit``
   package without import shadowing.

Known gaps before later migration phases
----------------------------------------

* The library package currently exposes only ``__version__`` and does not yet
   contain migrated business logic.
* The current CLI still runs from the legacy production implementation under
   ``src/multigit``.
* No publication step has been executed in this implementation session.
* Test ownership split between future library and CLI components is not yet
   implemented beyond this minimal PoC.
