#!/usr/bin/env python3
"""parsec's three hooks, named by hooks/hooks.json as ${CLAUDE_PLUGIN_ROOT}/tools/hooks.py <compact|agent|stop>. Fail open (D4): any error prints nothing and exits 0. Bytes in and out: a Windows text pipe re-encodes ledger.md.
compact: after a compaction in a session that launched a parsec skill, print the driver rule 3 line, then templates/driver-rules.md and templates/ledger.md (field audit 4, 2026-10-15: the reread held 2 of 31 times).
agent: deny a parsec: agent dispatch that sets model (Moving Day phase 10 tasks 16, 19 and 23 built on Sonnet).
stop: send the turn back once while no reply in the transcript holds the newest block the tool printed for posting (2026-10-04 Afterparty phases 2 to 4: 4 of 18 posted),
or while a round that round prepare named has its reply.md written and is not collected (2026-11-25 vc-arm0: the driver waited 3 h 51 min on a reply already on disk)."""
import ctypes, itertools, json, os, re, stat, sys   # one line, as in tools/parsec.py (Brandon, 2026-11-25: "Check for a cut first")
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent      # never the working directory
BAD = (ValueError, LookupError, TypeError, AttributeError, OSError, RecursionError)   # 2026-10-16 diff pre-review r1 (Opus F2), Sol diff r1: a bad record is skipped, and never hides a later one
PHRASE = "next: post the block above"                # tools/parsec.py ends a round block and a pre-flight with it; test_wiring counts the two
REPORT = "report path:"                              # round prepare prints it before an Opus or Fable round's reply.md (tools/parsec.py, prepare); test_inputs_and_preflight feeds that output to this hook
ROUND = re.compile(r"[A-Za-z]:(?:\\[^\\/:*?\"<>|\x00-\x1f]+)*\\rounds\\(?:design|prereview|diff|lastlook|panel)-r\d+-(?:opus|fable)")   # an agent round folder on a local drive, the shape of every field row (probe C6); never a UNC path, which Windows would open over the network
REL = re.compile(r"(?:panels\\)?[\w.-]+\\rounds\\(?:design|prereview|diff|lastlook|panel)-r\d+-(?:opus|fable)", re.ASCII)   # all the reason quotes of a late round: its last three names, with panels\ before a panel round's (Opus pre-review F2; only a panel round, Sol diff r1 F1), each in a strict set, so a cloned repository's folder name that holds text is never quoted (security review of v0.1.55, Brandon Q-H B); the hook runs no program and reads no project config
LATE = "reply.md is written and the round is not collected (pending.json is present) in "
RUN = "run round collect{} with --agent-id; --ran-ms is optional (without it the minutes count since prepare), so never wait for the notification."
GO_ON = 'this outranks the "post the block above in chat now" line each collect prints. If a reviewer is still running, or the next step waits on one, end the turn and wait for its hand-back.'


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
        content = record["attachment"]["prompt"] if record["type"] == "attachment" else record["message"]["content"]   # a task-notification that arrives mid-turn is a queued_command attachment with no message (Opus pre-review r1 F1; evidence/queued-command-shape.txt)
        if isinstance(content, str):                 # a task-notification is a source; a typed prompt never is
            return ([content] if content.startswith("<task-notification>") else []), []
        items = [content] if record["type"] == "assistant" else [block["content"] for block in content if block["type"] == "tool_result"]   # an assistant's blocks, or each tool result: a string (Bash) or text items (Read)
        found = [item if isinstance(item, str) else "\n".join(part["text"] for part in item if part["type"] == "text") for item in items]   # one text per tool result, its items joined in order (Sol F1); a text that is not a string raises here (Sol F2); thinking and tool_use blocks never count
        return ([], found) if record["type"] == "assistant" else (found, [])
    except BAD:
        return [], []


def local(folder):                                   # Sol diff r1 F1: a fixed drive (a mapped share is DRIVE_REMOTE) and no link or junction on the way, each part tested without following one
    parts = Path(folder).parts
    return ctypes.windll.kernel32.GetDriveTypeW(parts[0]) == 3 and not any(os.path.islink(p) or os.path.isjunction(p) for p in itertools.accumulate(parts[1:], os.path.join, initial=parts[0]))


def stop(event):                                     # 2026-10-17: the Sol R1 design block came in a task-notification and went to the author unposted
    head, owed, rounds = None, {}, set()             # owed: each heading printed for posting, true until a reply holds it (design r1, Sol F3); rounds: each folder a report path row names
    with open(event["transcript_path"], "rb") as transcript:   # one record in memory at a time
        for line in transcript:
            if PHRASE.encode() in line or b"### " in line or REPORT.encode() in line:   # filters only, they save parsing: a block holds the phrase, a post holds its heading, a prepare its report path
                sources, replies = texts(line)
                owed.update({h: False for h in owed if any(h in reply for reply in replies)})   # a reply that holds a heading posts that block
                for text in sources:
                    heading, path = None, None       # each source finds its own heading; a block split across records is missed (R1, Brandon SR-A)
                    for row in text.splitlines():
                        numbered = "\t" in row and row.partition("\t")[0].isdigit()   # a wrapped line of digits alone is no Read line (Astra diff r2 F13)
                        row = row.partition("\t")[2] if numbered else row.removeprefix("<event>").removesuffix("</event>")   # a Read result numbers each line; a Monitor event wraps its text (design r2, Sol F2)
                        path = row if not numbered and row.startswith(REPORT) else None if path is None else path + row   # a PowerShell wrap only inserts line breaks (probe C6); a new row drops an unclosed one; a Read copy begins none
                        if path is not None and path.strip().endswith("\\reply.md") and ROUND.fullmatch(folder := os.path.dirname(os.path.normpath(path[len(REPORT):].strip()))) and len(folder) < 260:   # normalised: a <name>\.. pair never reaches the reason; security review of 685a686: any tool result can print such a row, so only this shape is read or quoted; the join goes on, as a folder name can hold reply.md, even under a round-shaped folder (Astra diff r1 F2, r2 F2)
                            rounds.add(folder)
                        if row.startswith(("### 🔴", "### 🟡", "### 🟢", "### ⚪")) and len(row) < 200:   # X-A (Brandon, 2026-10-17; security review of 927de85): only the tool's heading shape, short, is quoted in the reason (tools/parsec.py: MARKERS, the round heading and the pre-flight heading), and beside it only a late round's last three names, in REL's strict set, whose folder holds pending.json and a non-empty reply.md; any other "### " line is no heading
                            heading = row.rstrip()
                        elif row.startswith(PHRASE) and heading and heading not in owed:   # every block in order (design r2, Sol F1); a line start, so a read of the tool's source has none
                            head = heading           # the newest block, the one the end checks; a heading seen before changes nothing
                            owed[head] = True
    late = []                                        # each feature\rounds\round, sorted by full path: two features' design-r1-fable stay apart, and round collect takes the feature; one folder printed in two casings is listed twice (R5, Sol diff r3 F12, F13)
    for folder in sorted(rounds):
        try:
            if REL.fullmatch(name := "\\".join((p := Path(folder).parts)[-4 if p[-4:-3] == ("panels",) and p[-1].startswith("panel-") else -3:])) and local(folder) and all(stat.S_ISREG((s := os.lstat(os.path.join(folder, n))).st_mode) for n in ("pending.json", "reply.md")) and s.st_size:   # lstat: a linked file is never followed (security review of 394c155); s is reply.md's
                late.append(name)
        except OSError:                              # a reply.md not yet written, or a folder another session's prepare renamed: that folder only is not late
            pass
    if event["stop_hook_active"]:                    # never on any Stop hook's continuation, ours or another plugin's (one shared flag); a missing key fails open
        return b""
    block, where = owed.get(head) and head not in (event.get("last_assistant_message") or ""), ", ".join(late)   # the transcript may lag the last reply, a field the CLI marks optional
    if block and late:                               # every post in one reply after the last collect: a post made before a tool call can be lost (below)
        reason = f'parsec: the block that starts "{head}" was printed for you to post, and no reply in the transcript holds that line; and {LATE}{where}. First, for each round whose reviewer has handed back, or with no hand-back has sent its task-notification, {RUN.format("")} Then, in one reply after the last collect, post the block that starts "{head}" (as is, outside a code block, with the additions the debate skill names; its heading line alone if a reply of this turn already holds it) and every block the collects printed, then go on with the flow\'s next step; {GO_ON}'
    elif late:                                       # 2026-11-25 vc-arm0: a reason that ended the turn after the collect would leave the session idle one step later
        reason = f"parsec: {LATE}{where}. For each round whose reviewer has handed back, or with no hand-back has sent its task-notification, {RUN.format(' now')} After the last collect, post every block the collects printed in one reply, then go on with the flow's next step; {GO_ON}"
    elif block:
        reason = f'parsec: the block that starts "{head}" was printed for you to post, and no reply in the transcript holds that line. If you posted it in this turn, reply with its heading line only, then end the turn. Otherwise post it now, as is and outside a code block, with the additions the debate skill names, then end the turn.'   # 2026-10-17: 4 of 9 posts made before a tool call were not saved, so the block was posted twice; a reply of its heading line clears it
    else:
        return b""
    return json.dumps({"decision": "block", "reason": reason}).encode("utf-8")


def main(argv):
    try:
        sys.stdout.buffer.write({"compact": compact, "agent": agent, "stop": stop}[argv[0]](json.loads(sys.stdin.buffer.read())))
    except Exception:                                # D4: fail open; nothing on stdout or stderr, and the script ends, exit 0
        pass


if __name__ == "__main__":
    main(sys.argv[1:])
