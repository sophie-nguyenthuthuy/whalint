import re

from whalint.registry import rule

_CD = re.compile(r"(?:^|&&|;)\s*cd\s+")


@rule("WL014", "cd inside RUN; use WORKDIR")
def run_cd(df):
    """'RUN cd /app && ...' only changes directory for that single RUN and
    hides the working directory from readers of later instructions.
    WORKDIR persists and documents itself.
    """
    for ins in df.of("RUN"):
        if ins.json_form is None and _CD.search(ins.value):
            yield ins
