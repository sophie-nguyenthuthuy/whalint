import re

from whalint.parser import parse_from
from whalint.registry import rule


@rule("WL001", "base image is not pinned (':latest' or no tag)")
def latest_tag(df):
    """An unpinned base image pulls whatever 'latest' means today, so the
    same Dockerfile builds different images on different days. Pin a tag
    (better: a digest). References to earlier build stages are exempt.
    """
    stages = set()
    for ins in df.of("FROM"):
        image, alias = parse_from(ins)
        exempt = (
            image.lower() in stages
            or image.lower() == "scratch"
            or image.startswith(("$", "${"))
            or "@" in image  # digest-pinned
        )
        if not exempt:
            last_segment = image.rsplit("/", 1)[-1]
            tag = last_segment.rsplit(":", 1)[1] if ":" in last_segment else None
            if tag is None or tag.lower() == "latest":
                yield ins, f"pin '{image}' to a specific tag or digest"
        if alias:
            stages.add(alias.lower())
