"""Run every registered rule over a Dockerfile and collect findings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Set

from whalint.parser import Instruction, parse
from whalint.registry import all_rules


@dataclass
class Finding:
    code: str
    message: str
    line: int
    detail: str = ""
    path: str = "Dockerfile"

    def text(self) -> str:
        tail = f" ({self.detail})" if self.detail else ""
        return f"{self.path}:{self.line}: {self.code} {self.message}{tail}"

    def as_dict(self) -> dict:
        return {
            "path": self.path,
            "line": self.line,
            "code": self.code,
            "message": self.message,
            "detail": self.detail,
        }


def lint(
    text: str,
    path: str = "Dockerfile",
    select: Optional[Set[str]] = None,
    ignore: Optional[Set[str]] = None,
) -> List[Finding]:
    df = parse(text)
    findings: List[Finding] = []
    for fn in all_rules():
        if select and fn.code not in select:
            continue
        if ignore and fn.code in ignore:
            continue
        if fn.code in df.file_ignores:
            continue
        for item in fn(df):
            detail = ""
            if isinstance(item, tuple):
                item, detail = item
            if isinstance(item, Instruction):
                if fn.code in item.ignores:
                    continue
                line = item.line
            else:
                line = int(item)
            findings.append(Finding(fn.code, fn.message, line, detail, path))
    return sorted(findings, key=lambda f: (f.line, f.code))
