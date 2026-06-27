"""Minimal public surface for the multigit-lib parity stage."""

from importlib import import_module
from typing import Any

__version__ = "0.0.1.dev2"

# Keep the package-level surface stable while modules are copied in later steps.
__all__ = [
	"__version__",
	"Gitrepo",
	"Subrepofile",
	"SubrepofileError",
]


def __getattr__(name: str) -> Any:
	if name == "Gitrepo":
		return getattr(import_module(".gitrepo", __name__), name)
	if name in {"Subrepofile", "SubrepofileError"}:
		return getattr(import_module(".subrepofile", __name__), name)
	raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
