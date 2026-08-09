import re

from whalint.registry import rule

_UPGRADE = re.compile(r"\bapt(-get)?\s+(?:[-\w.=]+\s+)*(dist-)?upgrade\b")


@rule("WL006", "apt upgrade inside the image")
def apt_upgrade(df):
    """Upgrading packages at build time makes the result depend on when it
    was built, not on what the Dockerfile says. Bump the base image tag
    instead -- that is what it is for.
    """
    for ins in df.of("RUN"):
        if _UPGRADE.search(ins.value):
            yield ins
