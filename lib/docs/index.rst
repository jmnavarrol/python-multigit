.. multigit-lib documentation master file.

.. toctree::
   :caption: Contents:
   :hidden:
   :maxdepth: 2

   genindex
   subrepofile
   subrepos
   gitrepo
   api
   testpypi_release_checklist_dev1

multigit-lib documentation
==========================
multigit-lib script and module.

:package: multigit-lib 0.0.2.dev1
:author: Jesús M. Navarro
:license: GNU General Public License v3.0
:source: https://github.com/jmnavarrol/python-multigit

.. automodule:: multigit_lib
  :noindex:
  :members:
  :undoc-members:
  :show-inheritance:

----

**multigit-lib** can also be used as an imported module.

**Classes:**
 * :ref:`Subrepofile<subrepofile>`: loads configuration from a subrepofile.
 * :ref:`SubrepofileError<subrepofile_error>`: Subrepofile's custom Exception.
 * :ref:`Subrepos<subrepos>`: processes a full subrepos' configuration.
 * :ref:`SubreposOrchestrationError<subrepos_orchestration_error>`: Subrepos orchestration custom Exception.
 * :ref:`Gitrepo<gitrepo>`: manages a single git repository as per the requested configuration.

Current Stage Boundaries
========================

In scope in ``lib/`` for this parity stage
------------------------------------------

* Package surface and versioning for transitional namespace ``multigit_lib``.
* Copied domain modules:

  * ``multigit_lib.gitrepo``
  * ``multigit_lib.subrepofile``
  * ``multigit_lib.subrepos_orchestration`` (library-safe orchestration slice)
* Schema/package data for subrepos loading.
* Offline component tests, including explicit legacy-vs-lib parity tests.
* Component-local Sphinx documentation and build/test packaging gates.

Out of scope in this stage (still in CLI/legacy)
-------------------------------------------------

* CLI entrypoint migration to consume ``multigit-lib``.
* Legacy runtime replacement under ``src/multigit``.
* Final architecture-purity refactors:

  * strict rendering separation
  * exception-model redesign
  * boundary/data-contract cleanup
* Further publication iterations (new versions and PyPI promotion) remain gated.

Transitional Notes
==================

* This stage prioritizes split ease and behavior parity over early architecture-purity refactors.
* Legacy-oriented behavior is intentionally preserved unless a packaging or test-unblocking change is strictly required.
* Refactors such as strict rendering separation, exception-model redesign, and boundary cleanup are deferred to post-split phases.

Current Status Summary
======================

* Library parity track is active and buildable.
* API documentation now reflects copied modules and exceptions.
* Root and legacy tests remain runnable during transition.
* Legacy source and tests remain in place until explicit retirement gates.
* TestPyPI publication completed for ``multigit-lib==0.0.2.dev1``.
