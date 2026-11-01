"""Reusable per-repository Git operations for multigit."""

from importlib import import_module
from typing import Any

__version__ = "0.0.2.dev4"

__all__ = [
	"__version__",
	"Gitrepo",
]


def __getattr__(name: str) -> Any:
	if name == "Gitrepo":
		return getattr(import_module(".gitrepo", __name__), name)
	raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
