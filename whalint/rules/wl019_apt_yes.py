import re

from whalint.registry import rule

_APT_INSTALL = re.compile(r"\bapt(-get)?\s+(?:[-\w.=]+\s+)*install\b")
_YES = re.compile(r"(^|\s)(-\w*y\w*|--yes|--assume-yes)(\s|$)")


@rule("WL019", "apt install without -y")
def apt_yes(df):
    """Docker builds have no TTY, so an interactive 'Do you want to
    continue?' prompt aborts the build -- but only once the cache reaches
    that layer, which makes it look intermittent.
    """
    for ins in df.of("RUN"):
        m = _APT_INSTALL.search(ins.value)
        if m and not _YES.search(ins.value):
            yield ins
