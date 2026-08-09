from whalint.registry import rule

_ARCHIVE_SUFFIXES = (
    ".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz", ".txz",
    ".tar.zst", ".gz", ".bz2", ".xz", ".zip",
)


def _needs_add(src: str) -> bool:
    low = src.lower()
    return low.startswith(("http://", "https://", "git@")) or low.endswith(_ARCHIVE_SUFFIXES)


@rule("WL002", "ADD used for a plain local file; use COPY")
def add_instead_of_copy(df):
    """ADD has magic behaviors (URL download, automatic archive extraction)
    that surprise readers and can pull remote content at build time. For
    plain local files COPY does the same thing with no surprises.
    """
    for ins in df.of("ADD"):
        args = ins.json_form or ins.value.split()
        sources = [a for a in args[:-1] if not a.startswith("--")]
        if sources and not any(_needs_add(s) for s in sources):
            yield ins
