from whalint.registry import rule


@rule("WL018", "COPY of the entire build context")
def copy_everything(df):
    """'COPY . .' copies everything in the context -- .git, local configs,
    stray secrets -- and invalidates this and every later layer whenever any
    file changes. Copy explicit paths, and keep a .dockerignore either way.
    """
    for ins in df.of("COPY"):
        args = ins.json_form or ins.value.split()
        sources = [a for a in args[:-1] if not a.startswith("--")]
        if any(s in (".", "./") for s in sources):
            yield ins
