import re

from whalint.registry import rule

_APT_INSTALL = re.compile(r"\bapt(-get)?\s+(?:[-\w.=]+\s+)*install\b")


@rule("WL005", "apt install without cleaning /var/lib/apt/lists in the same layer")
def apt_lists(df):
    """The package index downloaded by apt-get update lives in the layer
    forever unless it is removed in the same RUN. Append
    '&& rm -rf /var/lib/apt/lists/*'.
    """
    for ins in df.of("RUN"):
        if _APT_INSTALL.search(ins.value) and "/var/lib/apt/lists" not in ins.value:
            yield ins
