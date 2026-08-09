from whalint.registry import rule


@rule("WL020", "CMD/ENTRYPOINT in shell form; use JSON (exec) form")
def shell_form(df):
    """Shell form wraps the command in '/bin/sh -c', so PID 1 is the shell:
    the app never receives SIGTERM and every 'docker stop' waits out the
    10-second kill timeout. Write CMD [\"app\", \"--flag\"] instead.
    """
    for ins in df.of("CMD", "ENTRYPOINT"):
        if ins.json_form is None:
            yield ins
