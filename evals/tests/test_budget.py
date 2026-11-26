"""The weight budget (step 4 of the rethink; old items 60, 10 and 19: a check that passes when its input
is missing). Fails when a number passes its budget OR when any expected input is missing."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILLS = ["brainstorm", "build", "debate", "setup", "panel"]
# The Muse and Kimi lane notes (models/muse-*.md, models/kimi-*.md, lanes/kimi-reviewer.md) are read only when
# that lane runs, Muse as the backup and Kimi by name, so they are not counted (Brandon, 2026-10-15).
PROSE = [f"skills/{s}/SKILL.md" for s in SKILLS] + [
    "templates/driver-rules.md", "templates/spec.md", "templates/brief.md",
    "templates/brief-design.md", "templates/brief-diff.md", "templates/brief-lastlook.md", "templates/brief-panel.md", "templates/ledger.md",
    "agents/reviewer-opus.md", "agents/reviewer-fable.md",
    "agents/author.md", "commands/doctor.md", "models/index.md", "models/codex-cli.md",
    "models/astra.md", "models/fable.md", "models/opus.md", "models/sol.md",
    "models/agy-cli.md", "models/neon.md", "CLAUDE.md"]
CHECKERS = ["evals/tools/ste_lint.py", "evals/tools/ste_allow.txt", "evals/tools/check_changelog.py"]


def lines(path):
    assert path.is_file(), f"missing input: {path}"
    return len(path.read_text(encoding="utf-8").splitlines())


def words(path):
    assert path.is_file(), f"missing input: {path}"
    return len(path.read_text(encoding="utf-8").split())


def test_tool_within_1331_lines():
    assert lines(REPO / "tools" / "parsec.py") <= 1331   # Brandon, 2026-11-22: "A Raise to built count (Recommended)", the Trigger regrade (was 1,309)


def test_hooks_within_118_lines():
    assert lines(REPO / "tools" / "hooks.py") <= 118   # Brandon, 2026-11-25: "Not too worried about the budgets"; the built count of the late-round check, its round-shape guard and its local-drive check (direct-build B12; was 80)


def test_tests_within_1648_lines():
    tests = sorted((REPO / "evals" / "tests").glob("*.py"))
    assert tests, "missing input: the test folder"
    assert sum(lines(p) for p in tests) <= 1648   # Brandon, 2026-11-22, Q4: "A Raise to built count (Recommended)", the Trigger regrade test and its pre-review r1 and diff r1 fixes (was 1,596)


def test_frozen_checkers_do_not_grow():
    assert sum(lines(REPO / c) for c in CHECKERS) <= 522


def test_prose_within_15000_words_and_each_skill_within_1600():
    counts = {p: words(REPO / p) for p in PROSE}
    for s in SKILLS:
        assert counts[f"skills/{s}/SKILL.md"] <= 1600, (s, counts[f"skills/{s}/SKILL.md"])
    assert sum(counts.values()) <= 15000, sum(counts.values())   # Brandon, 2026-11-20: "B, raise to 15,000" (was 12,000)
