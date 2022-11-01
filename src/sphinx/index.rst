.. multigit documentation master file, created by
   sphinx-quickstart on Sat Aug 28 14:07:32 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

multigit documentation
======================

* :ref:`genindex`
* **Classes:**
   * :ref:`Subrepos<subrepos>`: *"main"* entrypoint for the full process.
   * :ref:`Gitrepo<gitrepo>`: manages a single git repository as per the requested configuration.

----

.. automodule:: multigit
   :noindex:
   :members:
   :undoc-members:
   :show-inheritance:

----

*"Main"* entry point is the `multigit` script:

.. command-output:: multigit --help

.. toctree::
   :caption: Contents:
   :hidden:
   :maxdepth: 2
   
   Class Subrepos <subrepos>
   Class Gitrepo <gitrepo>
