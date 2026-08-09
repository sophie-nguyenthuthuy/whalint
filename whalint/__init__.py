"""whalint -- a tiny Dockerfile linter where every rule is one small file."""

from whalint.engine import Finding, lint

__version__ = "0.1.0"
__all__ = ["lint", "Finding", "__version__"]
