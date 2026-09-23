"""The weight budget (step 4 of the rethink; old items 60, 10 and 19: a check that passes when its input
is missing). Fails when a number passes its budget OR when any expected input is missing."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILLS = ["brainstorm", "build", "debate", "setup", "panel"]
PROSE = [f"skills/{s}/SKILL.md" for s in SKILLS] + [
    "templates/driver-rules.md", "templates/spec.md", "templates/task-list.md", "templates/brief.md",
    "templates/brief-design.md", "templates/brief-diff.md", "templates/brief-panel.md", "templates/ledger.md",
    "templates/implementer-contract.md", "agents/backup-implementer.md", "agents/reviewer-opus.md", "agents/reviewer-fable.md",
    "agents/author.md", "lanes/kimi-reviewer.md", "commands/doctor.md", "models/index.md", "models/codex-cli.md",
    "models/kimi-cli.md", "models/astra.md", "models/kimi-k3.md", "models/fable.md", "models/opus.md", "models/sol.md",
    "models/agy-cli.md", "CLAUDE.md"]
CHECKERS = ["evals/tools/ste_lint.py", "evals/tools/ste_allow.txt", "evals/tools/check_changelog.py"]


def lines(path):
    assert path.is_file(), f"missing input: {path}"
    return len(path.read_text(encoding="utf-8").splitlines())


def words(path):
    assert path.is_file(), f"missing input: {path}"
    return len(path.read_text(encoding="utf-8").split())


def test_tool_within_1000_lines():
    assert lines(REPO / "tools" / "parsec.py") <= 1000


def test_tests_within_1500_lines():
    tests = sorted((REPO / "evals" / "tests").glob("*.py"))
    assert tests, "missing input: the test folder"
    assert sum(lines(p) for p in tests) <= 1500


def test_frozen_checkers_do_not_grow():
    assert sum(lines(REPO / c) for c in CHECKERS) <= 522


def test_prose_within_10000_words_and_each_skill_within_1600():
    counts = {p: words(REPO / p) for p in PROSE}
    for s in SKILLS:
        assert counts[f"skills/{s}/SKILL.md"] <= 1600, (s, counts[f"skills/{s}/SKILL.md"])
    assert sum(counts.values()) <= 10000, sum(counts.values())
