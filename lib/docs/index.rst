.. multigit-lib documentation master file.

.. toctree::
   :caption: Contents:
   :hidden:
   :maxdepth: 2

   genindex
   gitrepo
   api
   testpypi_release_checklist_dev1

multigit-lib documentation
==========================
multigit-lib script and module.

:package: multigit-lib 0.0.2.dev4
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
 * :ref:`Gitrepo<gitrepo>`: manages a single git repository as per the requested configuration.

Library Responsibilities
========================

The ``multigit-lib`` distribution owns per-repository Git status and update operations. It accepts normalized native repository configuration and does not read YAML files, discover ``subrepos`` files, or recurse through directory trees.

The Python import namespace is ``multigit_lib``. The CLI owns config-file discovery and parsing, recursive workflow, rendering, and exit-code decisions; it consumes ``Gitrepo`` through the installed library distribution.

Offline component tests cover repository status and update behavior, package import, and version exposure. Local Git fixtures keep the default suite offline.

Current Component Status
========================

* The CLI development distribution is ``multigit==0.12.0.dev6``. It owns configuration discovery, YAML parsing, recursive workflows, rendering, and exit-code decisions.
* The library development distribution is ``multigit-lib==0.0.2.dev4``. It owns per-repository Git status and update operations and imports as ``multigit_lib``.
* The CLI depends on ``multigit-lib>=0.0.2.dev4,<1`` through the installed distribution interface.
* The repository root contains shared guidance and orchestration only; runtime code, tests, package metadata, and API docs are component-owned.
* Development versions ``multigit==0.12.0.dev6`` and ``multigit-lib==0.0.2.dev4`` have not been published. Production PyPI publication remains blocked pending split-completion approval.
