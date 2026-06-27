# multigit-lib PoC

Minimal packaging PoC for the future library split.

This component currently validates build, test, and documentation workflows only.

TestPyPI upload is prepared but must not be executed unless explicitly approved.
Before running `make upload-tmp`, configure a `[testpypi]` entry in `~/.pypirc` with the credentials to be used by `twine upload --repository testpypi`.
