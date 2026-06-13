# multigit-lib
Reusable library for managing Git repositories within Git repositories.

## Overview
multigit-lib provides a Python library for recursive Git repository operations. It is the core library component of the [python-multigit](https://github.com/jmnavarrol/python-multigit) project, designed to be used independently in your own Python applications.

## Installation
```bash
pip install multigit-lib
```

[↑ Top](#multigit-lib)

## Quick Start
```python
from multigit import Gitrepo

# Create a repository configuration
repo_config = {
    'path': '/path/to/local/repo',
    'repo': 'https://github.com/owner/repo.git',
    'branch': 'main'
}

# Check repository status
git_ops = Gitrepo()
status = git_ops.status(repo_config)
print(status['status'])  # e.g., 'NOT_CLONED', 'UP_TO_DATE', 'PENDING_UPDATE'

# Update the repository
result = git_ops.update(repo_config)
print(result['status'])  # e.g., 'CLONED', 'UPDATED'
```

[↑ Top](#multigit-lib)

## API Reference

### Gitrepo Class
Handles individual Git repository operations.

#### `status(repoconf) → dict`
Determines the current status of a repository.

**Parameters:**
- `repoconf` (dict): Repository configuration with keys:
  - `path` (str, required): Local path to repository
  - `repo` (str, required): Git remote URL
  - `gitref_type` (str, optional): One of 'branch', 'tag', 'commit', or None
  - `branch/tag/commit` (str, optional): The specific reference to check out

**Returns:** Enhanced repoconf dict with added keys:
- `status` (str): Repository status
- `extra_info` (str, optional): Additional error or context information

**Status Values:**
- `NOT_CLONED`: Repository hasn't been cloned yet
- `UP_TO_DATE`: Local repository matches remote state
- `PENDING_UPDATE`: Repository needs to be cloned or updated
- `CLONED`: Repository was successfully cloned
- `UPDATED`: Repository was successfully updated
- `DIRTY`: Repository has uncommitted changes
- `EMPTY`: Remote repository hasn't been initialised
- `WRONG_REMOTE`: Repository points to a different remote
- `ERROR`: An error occurred during processing

#### `update(repoconf) → dict`
Attempts to update a repository based on its current status.

**Parameters:**
- `repoconf` (dict): Same format as `status()`

**Returns:** Enhanced repoconf dict with status after update attempt.

[↑ Top](#multigit-lib)

## Dependencies
- GitPython (for Git operations)

## Python Requirements
- Python 3.7 or newer

[↑ Top](#multigit-lib)

## Licence
This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

[↑ Top](#multigit-lib)

## See Also
- [multigit](https://github.com/jmnavarrol/python-multigit) – CLI distribution with full recursive subrepo support
- [python-multigit repository](https://github.com/jmnavarrol/python-multigit)
