from whalint.parser import parse, parse_from, parse_key_values


def test_continuations_join():
    df = parse("RUN apt-get update && \\\n    apt-get install -y curl\n")
    (run,) = df.instructions
    assert run.name == "RUN"
    assert run.value == "apt-get update && apt-get install -y curl"
    assert run.line == 1


def test_comment_inside_continuation_is_skipped():
    df = parse("RUN echo one && \\\n# a comment\n    echo two\n")
    (run,) = df.instructions
    assert "comment" not in run.value
    assert run.value.endswith("echo two")


def test_escape_directive():
    df = parse("# escape=`\nRUN echo one `\n    echo two\n")
    run = df.of("RUN")[0]
    assert run.value == "echo one echo two"


def test_json_form():
    df = parse('CMD ["python", "app.py"]\n')
    assert df.instructions[0].json_form == ["python", "app.py"]
    df = parse("CMD python app.py\n")
    assert df.instructions[0].json_form is None


def test_inline_ignore_attaches_to_next_instruction():
    df = parse("# whalint: ignore=WL003, WL015\nFROM x\nRUN echo hi\n")
    frm, run = df.instructions
    assert frm.ignores == frozenset({"WL003", "WL015"})
    assert run.ignores == frozenset()


def test_file_ignore():
    df = parse("# whalint: ignore-file=WL010\nFROM x\n")
    assert df.file_ignores == frozenset({"WL010"})


def test_parse_from():
    df = parse("FROM --platform=linux/amd64 python:3.12-slim AS build\n")
    image, alias = parse_from(df.instructions[0])
    assert image == "python:3.12-slim"
    assert alias == "build"


def test_parse_key_values_pair_form():
    assert parse_key_values('KEY=v OTHER="two words"') == [("KEY", "v"), ("OTHER", "two words")]


def test_parse_key_values_legacy_form():
    assert parse_key_values("KEY the whole rest") == [("KEY", "the whole rest")]


def test_parse_key_values_bare_arg():
    assert parse_key_values("TOKEN") == [("TOKEN", "")]
