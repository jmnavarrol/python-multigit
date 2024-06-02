.. multigit documentation master file, created by
   sphinx-quickstart on Sat Aug 28 14:07:32 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :caption: Contents:
   :hidden:
   :maxdepth: 2
   
   genindex
   subrepofile
   subrepos
   gitrepo

multigit documentation
======================
multigit script and module.

.. automodule:: multigit.__main__
   :noindex:
   :members:
   :undoc-members:
   :show-inheritance:

.. command-output:: multigit --help

----

**multigit** can also be used as an imported module.

**Classes:**
 * :ref:`Subrepofile<subrepofile>`: loads configuration from a subrepofile.
 * :ref:`SubrepofileError<subrepofile>`: Subrepofile's custom Exception.
 * :ref:`Subrepos<subrepos>`: processes a full subrepos' configuration.
 * :ref:`Gitrepo<gitrepo>`: manages a single git repository as per the requested configuration.
