from whalint.registry import rule


@rule("WL010", "image exposes ports but defines no HEALTHCHECK")
def no_healthcheck(df):
    """An EXPOSEd port says 'this is a service', but without a HEALTHCHECK
    the orchestrator can only see 'process still exists', not 'still
    serving'. An explicit 'HEALTHCHECK NONE' counts as a decision and is
    accepted.
    """
    if df.of("HEALTHCHECK"):
        return
    exposes = df.of("EXPOSE")
    if exposes:
        yield exposes[0]
