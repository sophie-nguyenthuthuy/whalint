"""Parse a Dockerfile into a flat list of instructions.

Line-oriented on purpose: handles continuations, comments (including the
``# escape=`` parser directive and inline ``# whalint: ignore=...`` markers),
and both shell- and JSON-form values. Not a full BuildKit parser -- it is
exactly as much parser as the rules need.
"""

from __future__ import annotations

import json
import re
import shlex
from dataclasses import dataclass, field
from typing import Iterator, List, Optional, Tuple

_DIRECTIVE_RE = re.compile(r"^#\s*escape\s*=\s*(\S)", re.IGNORECASE)
_IGNORE_RE = re.compile(r"whalint:\s*ignore\s*=\s*([A-Z0-9,\s]+)")
_IGNORE_FILE_RE = re.compile(r"whalint:\s*ignore-file\s*=\s*([A-Z0-9,\s]+)")


def _codes(blob: str) -> frozenset:
    return frozenset(c.strip() for c in blob.split(",") if c.strip())


@dataclass
class Instruction:
    name: str                     # uppercased keyword, e.g. "RUN"
    value: str                    # everything after the keyword, continuations joined
    line: int                     # 1-based line of the first physical line
    ignores: frozenset = frozenset()  # codes suppressed via preceding comment

    @property
    def json_form(self) -> Optional[list]:
        """The parsed JSON array for exec-form values, else None."""
        v = self.value.strip()
        if v.startswith("["):
            try:
                parsed = json.loads(v)
            except ValueError:
                return None
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        return None


@dataclass
class Dockerfile:
    instructions: List[Instruction] = field(default_factory=list)
    comments: List[str] = field(default_factory=list)

    def of(self, *names: str) -> List[Instruction]:
        wanted = {n.upper() for n in names}
        return [i for i in self.instructions if i.name in wanted]

    @property
    def file_ignores(self) -> frozenset:
        codes: set = set()
        for c in self.comments:
            m = _IGNORE_FILE_RE.search(c)
            if m:
                codes |= _codes(m.group(1))
        return frozenset(codes)


def parse(text: str) -> Dockerfile:
    lines = text.lstrip("﻿").splitlines()
    escape = "\\"
    for raw in lines:  # parser directives live in the leading comment block
        s = raw.strip()
        if not s.startswith("#"):
            break
        m = _DIRECTIVE_RE.match(s)
        if m:
            escape = m.group(1)

    df = Dockerfile()
    pending_ignores: set = set()
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("#"):
            df.comments.append(stripped)
            m = _IGNORE_RE.search(stripped)
            if m:
                pending_ignores |= _codes(m.group(1))
            i += 1
            continue

        start = i
        parts: List[str] = []
        while i < len(lines):
            cur = lines[i]
            cs = cur.strip()
            i += 1
            if parts and cs.startswith("#"):  # comment inside a continuation
                df.comments.append(cs)
                continue
            body = cur.rstrip()
            if body.endswith(escape) and not body.endswith(escape * 2):
                parts.append(body[:-1].strip())
                continue
            parts.append(cs)
            break

        joined = " ".join(p for p in parts if p)
        m = re.match(r"^([A-Za-z]+)\s*(.*)$", joined, re.DOTALL)
        if m:
            df.instructions.append(
                Instruction(
                    name=m.group(1).upper(),
                    value=m.group(2).strip(),
                    line=start + 1,
                    ignores=frozenset(pending_ignores),
                )
            )
        pending_ignores.clear()
    return df


# --- shared helpers for rules ------------------------------------------------

def parse_from(ins: Instruction) -> Tuple[str, Optional[str]]:
    """Return (image, stage_alias) for a FROM instruction."""
    tokens = [t for t in ins.value.split() if not t.startswith("--")]
    image = tokens[0] if tokens else ""
    alias = None
    if len(tokens) >= 3 and tokens[1].upper() == "AS":
        alias = tokens[2]
    return image, alias


def parse_key_values(value: str) -> List[Tuple[str, str]]:
    """Parse an ENV/ARG/LABEL body into (key, value) pairs.

    Handles both ``KEY=val KEY2="v 2"`` and the legacy ``KEY the whole rest``
    form, plus bare ``ARG NAME`` (value becomes "").
    """
    value = value.strip()
    if not value:
        return []
    head = value.split(None, 1)[0]
    if "=" not in head:
        key, _, rest = value.partition(" ")
        return [(key, rest.strip())]
    try:
        tokens = shlex.split(value)
    except ValueError:
        tokens = value.split()
    pairs: List[Tuple[str, str]] = []
    for tok in tokens:
        if "=" in tok:
            k, _, v = tok.partition("=")
            pairs.append((k, v))
        elif pairs:  # unquoted space in previous value
            k, v = pairs[-1]
            pairs[-1] = (k, (v + " " + tok).strip())
        else:
            pairs.append((tok, ""))
    return pairs


def shell_commands(value: str) -> Iterator[str]:
    """Split a shell-form RUN body on &&, ; and | into rough commands."""
    for cmd in re.split(r"&&|;|\|\||(?<!\|)\|(?!\|)", value):
        cmd = cmd.strip()
        if cmd:
            yield cmd
