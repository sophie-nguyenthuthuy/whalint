from whalint.registry import rule


@rule("WL003", "final image runs as root; add a non-root USER")
def root_user(df):
    """Docker's default user is root. A container escape or app compromise
    then hands the attacker uid 0. Create a user and switch to it in the
    final stage: RUN useradd -m app && ... USER app.
    """
    froms = df.of("FROM")
    if not froms:
        return
    final = froms[-1]
    users = [i for i in df.of("USER") if i.line > final.line]
    if not users:
        yield final, "no USER instruction after the final FROM"
    else:
        last = users[-1]
        who = last.value.strip().split(":")[0]
        if who in ("root", "0"):
            yield last, f"last USER is '{last.value.strip()}'"
