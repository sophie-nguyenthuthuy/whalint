import re

from whalint.parser import parse_key_values
from whalint.registry import rule

_SECRETY = re.compile(
    r"(PASSWORD|PASSWD|SECRET|TOKEN|API_?KEY|ACCESS_KEY|PRIVATE_KEY|CREDENTIALS?)",
    re.IGNORECASE,
)


@rule("WL008", "secret-looking value baked into ENV/ARG")
def secret_in_env(df):
    """ENV values live in the image config and ARG defaults in build history;
    'docker history' or any registry pull exposes them. Use build secrets
    (--mount=type=secret) or inject at runtime. Bare 'ARG TOKEN' with no
    default is fine and not flagged.
    """
    for ins in df.of("ENV", "ARG"):
        for key, value in parse_key_values(ins.value):
            if _SECRETY.search(key) and value and not value.startswith(("$", "${")):
                yield ins, f"'{key}' looks like a secret baked into the image"
