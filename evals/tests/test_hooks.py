"""Tests for tools/hooks.py and hooks/hooks.json (spec: dev/reviews/10-16-hooks). Field audit 4, 2026-10-15: the
reread after a compaction held 2 of 31 times, and Moving Day phase 10 tasks 16, 19 and 23 built on Sonnet because
a parsec dispatch set model. Each test runs the command that hooks/hooks.json names, so the wiring is under test."""
import json
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "tools" / "hooks.py"
REASON = ("parsec agents run with no model; the agent file names Brandon's choice (driver rule 1). "
          "Dispatch again without model.")
HEADER = b"driver rule 3: reread the skill in use and the feature's ledger and notes now"
SKILL_LINE = ('{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read","input":{"file_path":"a"}},'
              '{"type":"tool_use","name":"Skill","input":{"skill":"parsec:build"}}]}}')
TYPED_LINE = '{"type":"user","message":{"role":"user","content":"<command-message>parsec:build</command-message>\\n<command-name>/parsec:build</command-name>"}}'


def wiring():
    return json.loads((REPO / "hooks" / "hooks.json").read_text(encoding="utf-8"))


def hook(event, payload, script=None):
    """The command hooks.json names for the event; returns (exit code, stdout bytes, stderr bytes)."""
    argv = shlex.split(wiring()["hooks"][event][0]["hooks"][0]["command"].replace("${CLAUDE_PLUGIN_ROOT}", REPO.as_posix()))
    argv[0] = sys.executable
    if script:
        argv[1] = str(script)
    data = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
    proc = subprocess.run(argv, input=data, capture_output=True)
    return proc.returncode, proc.stdout, proc.stderr


def compact_event(tmp_path, *lines):
    path = tmp_path / "session.jsonl"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"session_id": "s", "transcript_path": str(path), "hook_event_name": "SessionStart", "source": "compact"}


def test_wiring():
    data = wiring()
    assert "hooks" in data and set(data) <= {"description", "hooks"}, sorted(data)   # the docs: without the wrapper the file fails to load
    assert sorted(data["hooks"]) == ["PreToolUse", "SessionStart"]
    for event, matcher, sub in (("SessionStart", "compact", "compact"), ("PreToolUse", "Agent|Task", "agent")):
        entry = data["hooks"][event][0]
        assert entry["matcher"] == matcher
        assert shlex.split(entry["hooks"][0]["command"]) == ["python", "${CLAUDE_PLUGIN_ROOT}/tools/hooks.py", sub]


def test_parsec_model_is_denied():
    code, out, err = hook("PreToolUse", {"tool_name": "Agent", "tool_input": {"subagent_type": "parsec:backup-implementer", "model": "sonnet"}})
    assert code == 0, err
    assert json.loads(out) == {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                      "permissionDecisionReason": REASON}}


@pytest.mark.parametrize("call", [{"subagent_type": "parsec:author"}, {"subagent_type": "parsec:author", "model": ""},
                                  {"subagent_type": "general-purpose", "model": "sonnet"}])
def test_dispatch_goes_ahead(call):
    assert hook("PreToolUse", {"tool_name": "Agent", "tool_input": call})[:2] == (0, b"")


@pytest.mark.parametrize("launch", [SKILL_LINE, TYPED_LINE])
def test_compaction_rereads_rules(tmp_path, launch):
    code, out, err = hook("SessionStart", compact_event(tmp_path, '{"type":"user"}', launch))
    rules = [(REPO / "templates" / name).read_bytes() for name in ("driver-rules.md", "ledger.md")]
    assert code == 0, err
    assert out == HEADER + b"\n\n" + rules[0] + b"\n" + rules[1]
    assert len(out.decode("utf-8")) < 10_000          # the harness cap; past it Claude gets a path and a preview


@pytest.mark.parametrize("line", [SKILL_LINE.replace("parsec:build", "superpowers:brainstorming"),
                                  SKILL_LINE.replace('"name":"Skill"', '"name":"Read"'),
                                  '{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read","input":{"example":'
                                  '{"type":"tool_use","name":"Skill","input":{"skill":"parsec:build"}}}}]}}',
                                  '{"type":"user","toolUseResult":' + SKILL_LINE + '}',
                                  TYPED_LINE.replace("parsec:build", "parsec:doctor"),
                                  TYPED_LINE.replace("<command-message>parsec:build</command-message>\\n", "see "),
                                  json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "content": json.loads(TYPED_LINE)["message"]["content"]}]}}),
                                  json.dumps({"type": "user", "content": 'the notes quote "skill":"parsec:build"'})])
def test_other_session_gets_nothing(tmp_path, line):
    assert hook("SessionStart", compact_event(tmp_path, line))[:2] == (0, b"")


@pytest.mark.parametrize("event,payload", [("SessionStart", b"not json"), ("PreToolUse", b"not json"),
                                           ("SessionStart", b"[]"), ("PreToolUse", b"[]"),
                                           ("SessionStart", {"source": "compact"}),
                                           ("SessionStart", {"transcript_path": "no/such/dir/session.jsonl"}),
                                           ("PreToolUse", {"tool_input": "x"})])
def test_fails_open(event, payload):
    assert hook(event, payload) == (0, b"", b"")


def test_missing_template_prints_nothing(tmp_path):
    for sub in ("tools", "templates"):
        (tmp_path / sub).mkdir()
    shutil.copyfile(SCRIPT, tmp_path / "tools" / "hooks.py")
    shutil.copyfile(REPO / "templates" / "driver-rules.md", tmp_path / "templates" / "driver-rules.md")
    assert hook("SessionStart", compact_event(tmp_path, SKILL_LINE), tmp_path / "tools" / "hooks.py") == (0, b"", b"")
