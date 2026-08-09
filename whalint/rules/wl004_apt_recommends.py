import re

from whalint.registry import rule

_APT_INSTALL = re.compile(r"\bapt(-get)?\s+(?:[-\w.=]+\s+)*install\b")


@rule("WL004", "apt install without --no-install-recommends")
def apt_recommends(df):
    """By default apt drags in every 'Recommends' dependency, easily doubling
    the layer size with packages the image never uses.
    """
    for ins in df.of("RUN"):
        if _APT_INSTALL.search(ins.value) and "--no-install-recommends" not in ins.value:
            yield ins
