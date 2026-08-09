from whalint.registry import rule


@rule("WL011", "EXPOSE 22 -- an SSH daemon does not belong in a container")
def expose_ssh(df):
    """Containers are entered with 'docker exec' / 'kubectl exec'. A sshd
    inside the image means key management, an extra attack surface, and a
    second init problem -- for a door you already have.
    """
    for ins in df.of("EXPOSE"):
        for port in ins.value.split():
            if port.split("/")[0] == "22":
                yield ins
                break
