TestPyPI publication checklist for 0.0.1.dev2
==============================================

Status
------

Published on TestPyPI. Version ``0.0.1.dev2`` is available at:

* https://test.pypi.org/project/multigit-lib/0.0.1.dev2/

Artifacts prepared
------------------

* dist/multigit_lib-0.0.1.dev2-py3-none-any.whl
* dist/multigit_lib-0.0.1.dev2.tar.gz

Artifact checksums (sha256)
---------------------------

* ecb64d39a8a859b9ea45afda40b46131d42bdbf862841f2c055d246eb4487d96  dist/multigit_lib-0.0.1.dev2-py3-none-any.whl
* 7f858204ab250d19b351d7832bdadcf184997c5ad736447fa8db7e31204ce370  dist/multigit_lib-0.0.1.dev2.tar.gz

Credentials and environment prerequisites
-----------------------------------------

1. A ``[testpypi]`` profile must exist in ``~/.pypirc`` for twine upload.
2. Account permissions for ``multigit-lib`` on TestPyPI must be confirmed.
3. The artifact version must be unique in TestPyPI (no overwrite attempts).
4. Build/test/doc gates must already be green before any publication action.

Publication command bundle (executed for 0.0.1.dev2)
-----------------------------------------------------

1. Validate artifacts:

   .. code-block:: bash

      python3 -m twine check dist/*

2. Upload to TestPyPI using Makefile helper:

   .. code-block:: bash

      make upload-tmp

3. Equivalent direct upload command:

   .. code-block:: bash

      python3 -m twine upload --repository testpypi dist/*

Post-upload verification bundle
-------------------------------

1. Verify package page shows the expected version and files.
2. Create a clean virtualenv and install from TestPyPI index.
3. Validate import and version.
4. Validate no ``multigit`` CLI command is installed by the library package.

Rollback / incident notes
-------------------------

1. TestPyPI artifacts are immutable; if incorrect artifacts are uploaded, publish a new dev version and deprecate usage of the bad one in release notes.
2. If upload succeeds but smoke verification fails, block CLI migration gate and record the issue in ``lib/CHANGELOG.md`` and top-level status docs.
3. Never reuse the same version identifier after a bad upload.
