"""Command-line interface: whalint [paths...]"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from whalint.engine import lint
from whalint.registry import all_rules

DOCKERFILE_GLOBS = ("Dockerfile", "Dockerfile.*", "*.Dockerfile", "Containerfile")


def find_dockerfiles(paths: List[str]) -> List[Path]:
    files: List[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            for pattern in DOCKERFILE_GLOBS:
                files.extend(path.rglob(pattern))
        else:
            raise FileNotFoundError(p)
    return sorted(set(f for f in files if f.is_file()))


def _codes(blob: str) -> set:
    return {c.strip().upper() for c in blob.split(",") if c.strip()}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        prog="whalint",
        description="A tiny, zero-dependency Dockerfile linter.",
    )
    ap.add_argument("paths", nargs="*", default=["."],
                    help="Dockerfiles or directories to search (default: .)")
    ap.add_argument("--select", default="", metavar="CODES",
                    help="comma-separated rule codes to run exclusively")
    ap.add_argument("--ignore", default="", metavar="CODES",
                    help="comma-separated rule codes to skip")
    ap.add_argument("--format", choices=("text", "json"), default="text")
    ap.add_argument("--list-rules", action="store_true",
                    help="print every rule with its explanation and exit")
    args = ap.parse_args(argv)

    if args.list_rules:
        for fn in all_rules():
            print(f"{fn.code}  {fn.message}")
            doc = (fn.__doc__ or "").strip()
            if doc:
                for ln in doc.splitlines():
                    print(f"       {ln.strip()}")
            print()
        return 0

    try:
        files = find_dockerfiles(args.paths or ["."])
    except FileNotFoundError as e:
        print(f"whalint: no such file or directory: {e}", file=sys.stderr)
        return 2
    if not files:
        print("whalint: no Dockerfiles found", file=sys.stderr)
        return 2

    findings = []
    for f in files:
        findings.extend(
            lint(
                f.read_text(encoding="utf-8", errors="replace"),
                path=str(f),
                select=_codes(args.select) or None,
                ignore=_codes(args.ignore) or None,
            )
        )

    if args.format == "json":
        print(json.dumps([f.as_dict() for f in findings], indent=2))
    else:
        for f in findings:
            print(f.text())
        if findings:
            n, files_n = len(findings), len({f.path for f in findings})
            print(f"\n{n} finding{'s' if n != 1 else ''} in {files_n} file{'s' if files_n != 1 else ''}.")
    return 1 if findings else 0
