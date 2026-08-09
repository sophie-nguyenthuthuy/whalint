from whalint.registry import rule


@rule("WL016", "multiple CMD/ENTRYPOINT instructions; only the last one wins")
def duplicate_cmd(df):
    """Docker silently uses only the final CMD and the final ENTRYPOINT in
    the file. Earlier ones are dead code that misleads readers.
    """
    for name in ("CMD", "ENTRYPOINT"):
        instructions = df.of(name)
        for ins in instructions[:-1]:
            yield ins, f"this {name} is overridden by the one on line {instructions[-1].line}"
