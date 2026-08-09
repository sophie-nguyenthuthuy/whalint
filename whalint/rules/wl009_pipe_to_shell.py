import re

from whalint.registry import rule

_PIPE_SH = re.compile(r"\b(curl|wget)\b[^|;&]*\|\s*(?:sudo\s+)?(?:ba|da|z|a)?sh\b")


@rule("WL009", "curl/wget piped straight into a shell")
def pipe_to_shell(df):
    """'curl ... | sh' executes whatever the server returns today, with no
    checksum and no review. Download, verify (sha256sum -c), then run.
    """
    for ins in df.of("RUN"):
        if _PIPE_SH.search(ins.value):
            yield ins
