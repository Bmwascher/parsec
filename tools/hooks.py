#!/usr/bin/env python3
"""parsec's three hooks, named by hooks/hooks.json as ${CLAUDE_PLUGIN_ROOT}/tools/hooks.py <compact|agent|stop>. Fail open (D4): any error prints nothing and exits 0. Bytes in and out: a Windows text pipe re-encodes ledger.md.
compact: after a compaction in a session that launched a parsec skill, print the driver rule 3 line, then templates/driver-rules.md and templates/ledger.md (field audit 4, 2026-10-15: the reread held 2 of 31 times).
agent: deny a parsec: agent dispatch that sets model (Moving Day phase 10 tasks 16, 19 and 23 built on Sonnet).
stop: send the turn back once while the newest block the tool printed for posting is not in chat (2026-10-04 Afterparty phases 2 to 4: 4 of 18 posted)."""
import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent      # never the working directory
BAD = (ValueError, LookupError, TypeError, AttributeError, OSError, RecursionError)   # 2026-10-16 diff pre-review r1 (Opus F2), Sol diff r1: a bad record is skipped, and never hides a later one
PHRASE = "next: post the block above"                # tools/parsec.py ends a round block and a pre-flight with it; test_wiring counts the two


def launched(line):                                  # 2026-10-16 design r1, r2 (Sol F1): a Skill block of the message itself, never data inside one
    try:
        blocks, skills = json.loads(line)["message"]["content"], [p.name for p in (PLUGIN / "skills").iterdir()]
        if isinstance(blocks, str):                  # 2026-10-16 Fable design r1 F1: a typed launch of a skill in skills/, never /parsec:doctor
            return blocks.startswith("<command-message>") and any(f"<command-name>/parsec:{s}</command-name>" in blocks for s in skills)
        return any(b["type"] == "tool_use" and b["name"] == "Skill" and b["input"]["skill"] in [f"parsec:{s}" for s in skills] for b in blocks)   # 0.1.30 last look F1: nor its Skill call
    except BAD:
        return False


def compact(event):
    with open(event["transcript_path"], "rb") as transcript:   # 2026-10-16 design r1 (Muse F2): one record in memory at a time
        launch = any((b'"skill":"parsec:' in line or b"<command-name>/parsec:" in line) and launched(line) for line in transcript)   # filters: a quoted copy is stored escaped; a typed /parsec:<name> is a user record with string content (evidence/typed-launch-shape.txt)
    return b"driver rule 3: reread the skill in use and the feature's ledger and notes now\n\n" + b"\n".join([(PLUGIN / "templates" / name).read_bytes() for name in ("driver-rules.md", "ledger.md")]) if launch else b""   # no launch reads no template; a list: both are read first, so a missing one prints nothing


def agent(event):
    call = event["tool_input"]
    if call.get("subagent_type", "").startswith("parsec:") and call.get("model"):
        return json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "parsec agents run with no model; the agent file names Brandon's choice (driver rule 1). Dispatch again without model."}}).encode("utf-8")
    return b""


def texts(line):                                     # one record's (sources, replies): a task-notification or tool results; an assistant record's text blocks
    try:
        record = json.loads(line)
        content = record["message"]["content"]
        if isinstance(content, str):                 # a task-notification is a source; a typed prompt never is
            return ([content] if content.startswith("<task-notification>") else []), []
        items = [content] if record["type"] == "assistant" else [block["content"] for block in content if block["type"] == "tool_result"]   # an assistant's blocks, or each tool result: a string (Bash) or text items (Read)
        found = [item if isinstance(item, str) else "\n".join(part["text"] for part in item if part["type"] == "text") for item in items]   # one text per tool result, its items joined in order (Sol F1); a text that is not a string raises here (Sol F2); thinking and tool_use blocks never count
        return ([], found) if record["type"] == "assistant" else (found, [])
    except BAD:
        return [], []


def stop(event):                                     # 2026-10-17: the Sol R1 design block came in a task-notification and went to the author unposted
    head, owed = None, {}                            # owed: each heading printed for posting, true until a reply holds it (design r1, Sol F3)
    with open(event["transcript_path"], "rb") as transcript:   # one record in memory at a time
        for line in transcript:
            if PHRASE.encode() in line or b"### " in line:   # filters only, they save parsing: a block holds the phrase, and a post holds its heading
                sources, replies = texts(line)
                owed.update({h: False for h in owed if any(h in reply for reply in replies)})   # a reply that holds a heading posts that block
                for text in sources:
                    heading = None                   # each source finds its own heading; a block split across records is missed (R1, Brandon SR-A)
                    for row in text.splitlines():
                        row = row.partition("\t")[2] if row.partition("\t")[0].isdigit() else row.removeprefix("<event>").removesuffix("</event>")   # a Read result numbers each line; a Monitor event wraps its text (design r2, Sol F2)
                        if row.startswith("### "):
                            heading = row.rstrip()
                        elif row.startswith(PHRASE) and heading and heading not in owed:   # every block in order (design r2, Sol F1); a line start, so a read of the tool's source has none
                            head = heading           # the newest block, the one the end checks; a heading seen before changes nothing
                            owed[head] = True
    if event["stop_hook_active"] or not owed.get(head) or head in (event.get("last_assistant_message") or ""):   # never on any Stop hook's continuation, ours or another plugin's (one shared flag); the transcript may lag the last reply, a field the CLI marks optional
        return b""
    return json.dumps({"decision": "block", "reason": f'parsec: the block that starts "{head}" was printed for you to post and is not in chat. Post it now, as is and outside a code block, with the additions the debate skill names, then end the turn.'}).encode("utf-8")


def main(argv):
    try:
        sys.stdout.buffer.write({"compact": compact, "agent": agent, "stop": stop}[argv[0]](json.loads(sys.stdin.buffer.read())))
    except Exception:                                # D4: fail open; nothing on stdout or stderr, and the script ends, exit 0
        pass


if __name__ == "__main__":
    main(sys.argv[1:])
