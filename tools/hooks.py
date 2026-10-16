#!/usr/bin/env python3
"""parsec's two hooks, named by hooks/hooks.json as ${CLAUDE_PLUGIN_ROOT}/tools/hooks.py <compact|agent>.
compact: after a compaction in a session that launched a parsec skill, print the driver rule 3 line, then
templates/driver-rules.md and templates/ledger.md (field audit 4, 2026-10-15: the reread held 2 of 31 times).
agent: deny a parsec: agent dispatch that sets model (Moving Day phase 10 tasks 16, 19 and 23 built on Sonnet).
Fail open (D4): any error prints nothing and exits 0. Bytes in and out: a Windows text pipe re-encodes ledger.md."""
import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent      # never the working directory
HEADER = b"driver rule 3: reread the skill in use and the feature's ledger and notes now"
REASON = "parsec agents run with no model; the agent file names Brandon's choice (driver rule 1). Dispatch again without model."
MARK = b'"skill":"parsec:'                           # a quoted copy is stored escaped, so it never matches
TYPED = b"<command-name>/parsec:"                    # a typed /parsec:<name>, a user record with string content (evidence/typed-launch-shape.txt)
TEMPLATES = ("driver-rules.md", "ledger.md")


def launched(line):                                  # 2026-10-16 design r1, r2 (Sol F1): a Skill block of the message itself, never data inside one
    try:
        blocks = json.loads(line)["message"]["content"]
        if isinstance(blocks, str):                  # 2026-10-16 Fable design r1 F1: a typed launch of a skill in skills/, never /parsec:doctor
            skills = [p.name for p in (PLUGIN / "skills").iterdir()]
            return blocks.startswith("<command-message>") and any(f"<command-name>/parsec:{s}</command-name>" in blocks for s in skills)
        return any(b["type"] == "tool_use" and b["name"] == "Skill" and b["input"]["skill"].startswith("parsec:") for b in blocks)
    except (ValueError, LookupError, TypeError, AttributeError, OSError, RecursionError):   # 2026-10-16 diff pre-review r1 (Opus F2), Sol diff r1: a bad record is no launch, and never hides a later one
        return False


def compact(event):
    with open(event["transcript_path"], "rb") as transcript:   # 2026-10-16 design r1 (Muse F2): one record in memory at a time
        if not any((MARK in line or TYPED in line) and launched(line) for line in transcript):
            return b""
    files = [(PLUGIN / "templates" / name).read_bytes() for name in TEMPLATES]   # both first: a missing one prints nothing
    return HEADER + b"\n\n" + b"\n".join(files)


def agent(event):
    call = event["tool_input"]
    if call.get("subagent_type", "").startswith("parsec:") and call.get("model"):
        decision = {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": REASON}
        return json.dumps({"hookSpecificOutput": decision}).encode("utf-8")
    return b""


def main(argv):
    try:
        event = json.loads(sys.stdin.buffer.read())
        sys.stdout.buffer.write({"compact": compact, "agent": agent}[argv[0]](event))
    except Exception:                                # D4: fail open; nothing on stdout or stderr, exit 0
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
