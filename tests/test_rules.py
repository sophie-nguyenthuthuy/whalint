"""The fixture walker.

Every rule gets tested automatically from tests/fixtures/<CODE>/:
  bad.Dockerfile   must trigger <CODE>
  good.Dockerfile  must NOT trigger <CODE>

Adding rule #21 therefore requires zero edits here -- drop the rule module
in whalint/rules/ and the two fixtures in tests/fixtures/WL021/, done.
"""

from pathlib import Path

import pytest

from whalint.engine import lint
from whalint.registry import all_rules

FIXTURES = Path(__file__).parent / "fixtures"
FIXTURE_CODES = sorted(p.name for p in FIXTURES.iterdir() if p.is_dir())


def codes_in(path: Path) -> set:
    return {f.code for f in lint(path.read_text())}


def test_registry_and_fixtures_match():
    """Every rule has a fixture directory, and vice versa."""
    rule_codes = sorted(fn.code for fn in all_rules())
    assert rule_codes == FIXTURE_CODES


def test_every_rule_documents_itself():
    for fn in all_rules():
        assert fn.__doc__ and fn.__doc__.strip(), f"{fn.code} has no docstring"
        assert fn.message, f"{fn.code} has no message"


@pytest.mark.parametrize("code", FIXTURE_CODES)
def test_bad_fixture_triggers(code):
    bad = FIXTURES / code / "bad.Dockerfile"
    assert bad.exists(), f"missing {bad}"
    assert code in codes_in(bad), f"{code} did not fire on its bad fixture"


@pytest.mark.parametrize("code", FIXTURE_CODES)
def test_good_fixture_is_clean(code):
    good = FIXTURES / code / "good.Dockerfile"
    assert good.exists(), f"missing {good}"
    assert code not in codes_in(good), f"{code} fired on its good fixture"
