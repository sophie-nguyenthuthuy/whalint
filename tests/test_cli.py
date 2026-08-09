import json

import pytest

from whalint.cli import main

BAD = "FROM ubuntu:latest\nCMD python app.py\n"
CLEAN = (
    "FROM python:3.12-slim\n"
    "RUN useradd --create-home app\n"
    "USER app\n"
    'CMD ["python", "app.py"]\n'
)


@pytest.fixture
def bad_file(tmp_path):
    p = tmp_path / "Dockerfile"
    p.write_text(BAD)
    return p


def test_findings_exit_1(bad_file, capsys):
    assert main([str(bad_file)]) == 1
    out = capsys.readouterr().out
    assert "WL001" in out and "WL020" in out


def test_clean_exit_0(tmp_path):
    p = tmp_path / "Dockerfile"
    p.write_text(CLEAN)
    assert main([str(p)]) == 0


def test_select(bad_file, capsys):
    assert main([str(bad_file), "--select", "WL001"]) == 1
    out = capsys.readouterr().out
    assert "WL001" in out and "WL020" not in out


def test_ignore_flag(bad_file, capsys):
    main([str(bad_file), "--ignore", "WL001,WL003,WL020"])
    assert "WL001" not in capsys.readouterr().out


def test_inline_ignore(tmp_path, capsys):
    p = tmp_path / "Dockerfile"
    p.write_text("# whalint: ignore=WL001\n" + BAD)
    main([str(p)])
    assert "WL001" not in capsys.readouterr().out


def test_json_format(bad_file, capsys):
    main([str(bad_file), "--format", "json"])
    findings = json.loads(capsys.readouterr().out)
    assert any(f["code"] == "WL001" for f in findings)
    assert all({"path", "line", "code", "message"} <= set(f) for f in findings)


def test_directory_discovery(tmp_path):
    (tmp_path / "svc").mkdir()
    (tmp_path / "svc" / "api.Dockerfile").write_text(BAD)
    assert main([str(tmp_path)]) == 1


def test_missing_path_exit_2(tmp_path):
    assert main([str(tmp_path / "nope")]) == 2


def test_list_rules(capsys):
    assert main(["--list-rules"]) == 0
    out = capsys.readouterr().out
    assert out.count("WL0") >= 20
