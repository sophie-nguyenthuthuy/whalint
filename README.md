# whalint 🐋

A tiny, **zero-dependency** Dockerfile linter where **every rule is one small file**.

Docker's defaults are famously wrong for production: root user, `:latest` tags,
shell-form CMD that eats SIGTERM, apt caches shipped in layers. whalint ships 20
rules that catch them — and is built so that contributing rule #21 is a ~30-line
file plus two fixtures, with **zero edits anywhere else**.

```console
$ whalint Dockerfile
Dockerfile:1: WL001 base image is not pinned (':latest' or no tag) (pin 'node:latest' to a specific tag or digest)
Dockerfile:1: WL003 final image runs as root; add a non-root USER (no USER instruction after the final FROM)
Dockerfile:7: WL015 sudo inside RUN
Dockerfile:10: WL020 CMD/ENTRYPOINT in shell form; use JSON (exec) form
...
15 findings in 1 file.
```

## Install

```bash
pip install whalint          # no dependencies, pure stdlib
```

Or just vendor it — it is stdlib-only Python ≥ 3.9.

## Usage

```bash
whalint                       # lint every Dockerfile under .
whalint path/to/Dockerfile    # lint one file
whalint --select WL001,WL003  # only these rules
whalint --ignore WL010        # skip a rule
whalint --format json         # machine-readable output
whalint --list-rules          # every rule with its full explanation
```

Exit codes: `0` clean, `1` findings, `2` usage error. Drop it straight into CI.

### Suppressing a finding

```dockerfile
# whalint: ignore=WL003
FROM postgres:16          # this instruction only

# whalint: ignore-file=WL010
```

## The rules

| Code | What it catches |
|------|-----------------|
| WL001 | Base image unpinned (`:latest` or no tag) |
| WL002 | `ADD` where `COPY` suffices |
| WL003 | Final image runs as root (no/`root` USER) |
| WL004 | apt install without `--no-install-recommends` |
| WL005 | apt cache (`/var/lib/apt/lists`) shipped in the layer |
| WL006 | `apt upgrade` baked into the build |
| WL007 | `pip install` without `--no-cache-dir` (ENV-aware) |
| WL008 | Secret-looking values in `ENV`/`ARG` |
| WL009 | `curl \| sh` — unverified remote code execution |
| WL010 | Ports exposed but no `HEALTHCHECK` |
| WL011 | `EXPOSE 22` — sshd in a container |
| WL012 | Deprecated `MAINTAINER` |
| WL013 | Relative `WORKDIR` |
| WL014 | `cd` in `RUN` instead of `WORKDIR` |
| WL015 | `sudo` in `RUN` |
| WL016 | Duplicate `CMD`/`ENTRYPOINT` (only the last wins) |
| WL017 | `apk add` without `--no-cache` |
| WL018 | `COPY . .` — whole build context, cache-buster |
| WL019 | apt install without `-y` (hangs the build) |
| WL020 | Shell-form `CMD`/`ENTRYPOINT` (PID 1 never sees SIGTERM) |

`whalint --list-rules` prints the *why* for each — every rule carries its own
explanation in its docstring.

## Writing rule #21

A rule is one file in `whalint/rules/`. It is auto-discovered — no registration
list, no imports to add, no test to write:

```python
# whalint/rules/wl021_npm_install.py
import re

from whalint.registry import rule

_NPM_INSTALL = re.compile(r"\bnpm\s+(install|i)\b")


@rule("WL021", "npm install in an image build; use npm ci")
def npm_install(df):
    """npm install may rewrite the lockfile and resolve different versions
    on different days. npm ci installs exactly what package-lock.json says,
    faster, and fails loudly when the lockfile is stale.
    """
    for ins in df.of("RUN"):
        if _NPM_INSTALL.search(ins.value):
            yield ins
```

Add `tests/fixtures/WL021/bad.Dockerfile` and `good.Dockerfile`, run `pytest` —
the fixture walker picks the new rule up automatically. Full walkthrough in
[CONTRIBUTING.md](CONTRIBUTING.md).

## Design

- **Parser** ([whalint/parser.py](whalint/parser.py)) — line-oriented Dockerfile parser: continuations,
  comments, `# escape=` directive, JSON/shell form, inline ignores. As much
  parser as the rules need and no more.
- **Registry** ([whalint/registry.py](whalint/registry.py)) — `@rule(code, message)` + `pkgutil`
  auto-discovery of everything in `whalint/rules/`.
- **Engine** ([whalint/engine.py](whalint/engine.py)) — runs rules, applies inline/file/CLI
  suppressions, sorts findings.
- Rules yield instructions (or line numbers); the framework does the rest.

## License

MIT
