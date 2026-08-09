import re

from whalint.registry import rule

_APK_ADD = re.compile(r"\bapk\s+(?:[-\w]+\s+)*add\b")


@rule("WL017", "apk add without --no-cache")
def apk_cache(df):
    """Without --no-cache, apk leaves its package index in /var/cache/apk
    inside the layer. '--no-cache' fetches the index transiently and is the
    single-flag replacement for the old 'update + add + rm cache' dance.
    """
    for ins in df.of("RUN"):
        if _APK_ADD.search(ins.value) and "--no-cache" not in ins.value:
            yield ins
