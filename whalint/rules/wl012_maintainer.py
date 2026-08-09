from whalint.registry import rule


@rule("WL012", "MAINTAINER is deprecated; use a LABEL")
def maintainer(df):
    """MAINTAINER has been deprecated since Docker 1.13 (2017). Use
    'LABEL org.opencontainers.image.authors="..."' which is queryable
    like any other label.
    """
    for ins in df.of("MAINTAINER"):
        yield ins
