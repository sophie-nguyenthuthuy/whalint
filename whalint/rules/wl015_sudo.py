import re

from whalint.registry import rule

_SUDO = re.compile(r"(?:^|&&|;|\|)\s*sudo\b")


@rule("WL015", "sudo inside RUN")
def sudo(df):
    """Build steps already run as root (until USER says otherwise), so sudo
    is at best a no-op and at worst an extra setuid binary with known CVE
    history shipped in the image. Reorder around USER instead.
    """
    for ins in df.of("RUN"):
        if ins.json_form is None and _SUDO.search(ins.value):
            yield ins
