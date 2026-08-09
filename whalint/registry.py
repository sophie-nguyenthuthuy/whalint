"""The rule registry.

A rule is a plain function decorated with @rule(code, message). It receives a
parsed ``Dockerfile`` and yields findings:

    yield ins                    # an Instruction (line + inline-ignore aware)
    yield ins, "extra detail"    # same, with a per-finding detail string
    yield 12                     # a bare line number (for file-level rules)
    yield 12, "extra detail"

Rules live one-per-file in whalint/rules/ and are discovered automatically.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import Callable, Dict, List

_RULES: Dict[str, Callable] = {}
_discovered = False


def rule(code: str, message: str) -> Callable:
    def deco(fn: Callable) -> Callable:
        if code in _RULES:
            raise ValueError(f"duplicate rule code {code}")
        fn.code = code
        fn.message = message
        _RULES[code] = fn
        return fn

    return deco


def all_rules() -> List[Callable]:
    """Import every module in whalint.rules once, then return rules by code."""
    global _discovered
    if not _discovered:
        import whalint.rules as pkg

        for mod in pkgutil.iter_modules(pkg.__path__):
            importlib.import_module(f"{pkg.__name__}.{mod.name}")
        _discovered = True
    return [_RULES[c] for c in sorted(_RULES)]
