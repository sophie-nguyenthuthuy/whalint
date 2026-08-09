from whalint.registry import rule


@rule("WL013", "WORKDIR is a relative path")
def relative_workdir(df):
    """A relative WORKDIR resolves against whatever the previous WORKDIR
    happened to be -- including one inherited from the base image. Use an
    absolute path so the location is explicit.
    """
    for ins in df.of("WORKDIR"):
        path = ins.value.strip().strip('"').strip("'")
        if path and not path.startswith(("/", "$", "${")):
            yield ins, f"'{path}' resolves against the previous WORKDIR"
