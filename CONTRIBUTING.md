# Contributing a rule

The whole point of whalint's architecture is that a new rule touches exactly
three new files and zero existing ones. Here is the complete process, using a
real example: flagging `npm install` where `npm ci` belongs.

## 1. Pick a code

Take the next free `WLxxx`. Codes are never reused or renumbered.

## 2. Write the rule — one file

Create `whalint/rules/wl021_npm_install.py`:

```python
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

That's the entire rule. Notes:

- `df` is a parsed `Dockerfile`; `df.of("RUN")` returns instructions by name.
  Continuation lines are already joined; `ins.value` is the full body,
  `ins.line` the first physical line, `ins.json_form` the parsed exec-form
  array (or `None` for shell form).
- Yield an `Instruction` to report it. Yield `(ins, "detail")` to add a
  per-finding detail string. File-level rules can yield a bare line number.
- The **docstring is user-facing** — `whalint --list-rules` prints it. Say
  *why* the pattern is a problem and what to do instead. A rule without a
  docstring fails the test suite.
- Helpers `parse_from`, `parse_key_values`, and `shell_commands` live in
  `whalint.parser`.
- Prefer false negatives over false positives. A linter that cries wolf gets
  uninstalled. If a pattern has a legitimate escape hatch (like
  `HEALTHCHECK NONE` for WL010), honor it.

## 3. Add fixtures — two files

```dockerfile
# tests/fixtures/WL021/bad.Dockerfile
FROM node:22-slim
RUN npm install
```

```dockerfile
# tests/fixtures/WL021/good.Dockerfile
FROM node:22-slim
RUN npm ci
```

`bad.Dockerfile` must trigger your code; `good.Dockerfile` must not. The good
fixture should be the *fixed version* of the bad one — it doubles as
documentation of the recommended pattern. Other rules firing on your fixtures
is fine; the walker only asserts on your code.

## 4. Run the tests

```bash
python -m pytest
```

There is nothing to register and no test to write. `tests/test_rules.py`
discovers your fixture directory, checks bad triggers / good doesn't, verifies
the registry and fixture tree match one-to-one, and requires the docstring.

## 5. Open the PR

One rule per PR. Include in the description a real-world Dockerfile (a link is
fine) that your rule would have caught.
