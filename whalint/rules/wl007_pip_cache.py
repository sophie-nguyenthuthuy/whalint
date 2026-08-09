import re

from whalint.parser import parse_key_values
from whalint.registry import rule

_PIP_INSTALL = re.compile(r"\bpip[0-9.]*\s+install\b")


@rule("WL007", "pip install without --no-cache-dir")
def pip_cache(df):
    """pip's wheel cache is useless inside an image but still ships in the
    layer. Pass --no-cache-dir (or set ENV PIP_NO_CACHE_DIR=1 once, which
    this rule detects and accepts).
    """
    for env in df.of("ENV"):
        if any(k == "PIP_NO_CACHE_DIR" for k, _ in parse_key_values(env.value)):
            return
    for ins in df.of("RUN"):
        if _PIP_INSTALL.search(ins.value) and "--no-cache-dir" not in ins.value:
            yield ins
