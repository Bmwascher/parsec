#!/usr/bin/env python3
"""parsec: the debate round as a tool. Standard library only, one file.

Skills, commands and agents name this file as ${CLAUDE_PLUGIN_ROOT}/tools/parsec.py
(2026-08-16: an agent that searched the disk ran the oldest of ten cached copies).
No shell parses a prompt: every CLI starts from an argument list, the brief reaches
codex on standard input as bytes, and the tool finds lanes.toml and lanes/ from __file__.
Every dated comment names the failure the line prevents; the design is step 4 of the
rethink notes (2026-09-22)."""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent
LANES_FILE = PLUGIN / "lanes.toml"             # a test points this at a file that names a fake CLI
POLL_SECONDS = 30                              # the watcher's period; a test overrides it
CAP_SECONDS = 28 * 60                          # Brandon's cap, no config key; a test overrides it
STILL_MINUTES = (10, 15, 20, 25)
KINDS = ("design", "prereview", "diff", "lastlook", "panel")
CLI_LANES = ("astra", "sol", "kimi")
AGENT_OF = {"opus": "reviewer-opus", "fable": "reviewer-fable"}
VERDICTS = ("PASS", "FIX", "ESCALATE", "BLIND")
CODEX_FLAGS = ["exec", "--sandbox", "read-only",                     # 2026-07-24: a resumed round lost its sandbox and wrote
               "--disable", "plugins", "--disable", "apps",           # 2026-07-28: sources on the reviewer's machine steered a review
               "--disable", "memories",                               # 2026-08-12: observed on without it; free
               "-c", "mcp_servers.node_repl.enabled=false"]           # 2026-08-11: the JavaScript tool was left on by two flags
CLOSING = ("Do not run commands or attempt verification: the test steps, the commit step and "
           "everything after the file edits are not yours; your only job is the file edits.")
ROUTE_LINES = ("Print mode: starting", "Propagating selected model override", "applying agent mode accept-edits")
SOFT_DENY = "soft-denying tool confirmation"
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


class Exit(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def now():
    return dt.datetime.now().astimezone()


def stamp(t=None):
    return (t or now()).isoformat(timespec="microseconds")   # records and amendments sort by this


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_text(path):
    return Path(path).read_text(encoding="utf-8", errors="replace")


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def git(args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", creationflags=NO_WINDOW)


def git_out(args, cwd):
    r = git(args, cwd)
    if r.returncode:
        raise Exit(64, f"git {' '.join(args)} failed in {cwd}: {r.stderr.strip()[-300:]}")
    return r.stdout


def worktree_list(repo):
    return [Path(l[9:].strip()) for l in git_out(["worktree", "list", "--porcelain"], repo).splitlines()
            if l.startswith("worktree ")]


def primary_of(repo):
    trees = worktree_list(repo)     # the FIRST entry is the primary; --git-common-dir breaks on a separate git dir
    if not trees:
        raise Exit(64, f"{repo} is not inside a git repository")
    return trees[0]


def resolve_under(base, p):
    p = Path(str(p).replace("\\", os.sep))
    return (p if p.is_absolute() else Path(base) / p).resolve()


def load_config(primary):
    path = Path(primary) / ".claude" / "parsec.toml"
    if not path.is_file():                      # old item 100: four docs roots because each writer guessed
        raise Exit(64, f"no config at {path}: run setup first")
    cfg = tomllib.loads(path.read_text(encoding="utf-8-sig"))
    for key in ("docs_root", "worktrees"):
        if key not in cfg:
            raise Exit(64, f"config {path} has no {key}: run setup first")
    return cfg


def lanes():
    return tomllib.loads(Path(LANES_FILE).read_text(encoding="utf-8-sig"))


def lane_row(name):
    rows = lanes()
    if name not in rows:
        raise Exit(64, f"lane {name} is not in {LANES_FILE}")
    return rows[name]


def agent_seat(lane):
    """A Claude seat's model and effort live in its agent file, the one authority."""
    text = read_text(PLUGIN / "agents" / f"{AGENT_OF[lane]}.md")
    head = text.split("---")[1] if text.startswith("---") else ""
    keys = dict(re.findall(r"^(\w+):\s*(.+?)\s*$", head, re.M))
    return keys.get("model", "unknown"), keys.get("effort", "unknown"), AGENT_OF[lane]


def is_link(p):
    return Path(p).is_symlink() or Path(p).is_junction()


def child_env():
    env = {k: v for k, v in os.environ.items() if k != "CODEX_HOME"}   # 2026-07-24: a redirected home read "Not logged in"
    env["NO_COLOR"] = "1"
    return env


def installed_entry():
    """(marketplace, entry) of the installed parsec, or (None, {})."""
    f = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    for key, val in (read_json(f).get("plugins", {}) if f.is_file() else {}).items():
        if key.startswith("parsec@"):
            return key.split("@", 1)[1], (val[0] if isinstance(val, list) else val)
    return None, {}


def behind():
    """2026-09-23: three phase sessions ran 0.1.6 for hours after 0.1.7 was installed; a skill names the path it loaded."""
    try:
        mine, inst = read_json(PLUGIN / ".claude-plugin" / "plugin.json")["version"], installed_entry()[1].get("version")
        key = lambda v: tuple(int(x) for x in v.split("."))
        return f"this tool is parsec {mine}, but {inst} is installed: invoke the skill again so it names the new path" if inst and key(inst) > key(mine) else None
    except (OSError, ValueError, KeyError, AttributeError):
        return None


# ---------------------------------------------------------------- feature, records, replies

def feature_dir(cfg, primary, feature, first=None):
    """A missing panels/<name> passes only for prepare's round 1 (`first`); prepare makes it after its checks."""
    docs = resolve_under(primary, cfg["docs_root"])
    whole = resolve_under(primary, feature)      # 2026-09-23: "dev/docs/parsec/<x>" was refused by round run, accepted by doctor
    rel = whole.relative_to(docs) if whole.is_relative_to(docs) and whole != docs else Path(feature.replace("\\", "/"))
    fdir = docs / rel
    if docs not in fdir.resolve().parents:       # 2026-09-22 review (Sol): "../x" reached past the docs root
        raise Exit(64, f"--feature {feature} is not under the docs root {docs}")
    panel = rel.parts[:1] == ("panels",) and len(rel.parts) == 2
    if not fdir.is_dir() and not (panel and first == 1):   # 2026-09-23 last look: collect and close made a mistyped panel folder
        raise Exit(64, f"feature folder {fdir} does not exist" + (": a new panel's first round is 1" if panel and first is not None else " (a mistyped name must not grow a second docs root)"))
    return fdir, rel.as_posix()


def round_folder(fdir, kind, n, lane):
    return fdir / "rounds" / f"{kind}-r{n}-{lane}"


def dead_rename(path):
    """Rename to <name>.dead<k>; the brief that was really sent and any stale reply leave the way."""
    k = 1
    while path.with_name(f"{path.name}.dead{k}").exists():
        k += 1
    path.rename(path.with_name(f"{path.name}.dead{k}"))
    return k


def records(fdir):
    """Every record and amendment under rounds\\, dead attempts included, oldest first."""
    out = []
    rounds = fdir / "rounds"
    if rounds.is_dir():
        for p in list(rounds.glob("*/record.json")) + list(rounds.glob("amendment-*.json")):
            r = read_json(p)
            r["_path"] = str(p)
            out.append(r)
    return sorted(out, key=lambda r: r.get("end") or r.get("time") or "")


def strip_line(line):
    return re.sub(r"^[\s\-\*>#]*\**", "", line).strip()


def tag_line(text, tag):
    """The last line that, after bullets and asterisks, STARTS with the tag; None when there is none."""
    for line in reversed(text.splitlines()):
        s = strip_line(line)
        if s.upper().startswith(tag + ":"):
            return s[len(tag) + 1:].strip(" *")
    return None


def verdict_of(text):
    """Old item 34: a truncated reply must read NONE, and a reviewer echoing the brief's instruction
    then cut off must not read as PASS, so a line naming more than one verdict word is ignored."""
    for line in reversed(text.splitlines()):
        s = strip_line(line)
        if not s.upper().startswith("VERDICT:"):
            continue
        words = set(re.findall(r"\b(PASS|FIX|ESCALATE|BLIND)\b", s.upper()))
        rest = s[8:].strip(" *").upper()
        for w in VERDICTS:
            if rest.startswith(w) and words == {w}:
                return w
    return "NONE"


def ledger_line(fdir, text, warnings):
    try:
        with open(fdir / "ledger.md", "a", encoding="utf-8", newline="\n") as f:
            f.write(f"- {now().strftime('%Y-%m-%d %H:%M %z')} {text}\n")
    except OSError as e:                        # a failed append is a warning, never a traceback
        warnings.append(f"ledger append failed: {e}")


# ---------------------------------------------------------------- the package

def heading_index(path):
    return [re.sub(r"\s+#*$", "", m.group(1)).strip() for m in
            re.finditer(r"^#+\s+(.+?)\s*$", read_text(path), re.M)]


def context_lines(cfg, primary, reference):
    """One function for the pre-flight and for context.md: rubric sections, lookups, the reference."""
    lines, warnings, found, wanted = [], [], 0, 0
    for c in cfg.get("context", []):
        path = resolve_under(primary, c["path"])
        role = c.get("role", "rubric")
        if role == "reference-code":
            if reference:
                lines.append(f"- reference code (a port or a module with a reference): {path / reference}")
            continue
        if role == "lookup":
            lines.append(f"- look up and cite only: {path}")
            continue
        heads = heading_index(path) if path.is_file() else []
        secs = c.get("sections", [])
        wanted += len(secs)
        if not path.is_file():
            warnings.append(f"rubric file not found: {path}")
            wanted += 1                          # a missing file fails the pre-flight like a missing section (2026-09-22 review)
        for s in secs:
            if s in heads:
                found += 1
            else:
                warnings.append(f'rubric section not found: "{s}" in {path}')
        lines.append(f"- read first: {path}" + (f", sections: {'; '.join(secs)}" if secs else ""))
    return lines, warnings, found, wanted


def write_package(root, args, cfg, primary, fdir, kind):
    """The package folder .parsec\\ at root; returns the subject hashes and the warnings."""
    pkg = root / ".parsec"
    if pkg.exists():
        shutil.rmtree(pkg)
    pkg.mkdir(parents=True)
    shutil.copyfile(args.brief, pkg / "brief.md")                          # the same bytes
    lines, warnings, _, _ = context_lines(cfg, primary, args.reference)
    ev = [(pkg / "evidence" / f"{k}-{src.name}", src) for k, src in enumerate([Path(f).resolve() for f in args.file or []], 1)]   # checked in prepare
    lines += [f"- evidence: .parsec/evidence/{dst.name} is a copy of {src}" for dst, src in ev]   # 2026-09-23: a reviewer looked for notes.md by its own name
    (pkg / "context.md").write_text("# Context\n\n" + ("\n".join(lines) or "(none configured)") + "\n",
                                    encoding="utf-8", newline="\n")
    subject = {}
    if kind == "design":
        for name in ("spec.md", "tasks.md"):     # both checked in prepare, before anything is written
            src = fdir / name
            shutil.copyfile(src, pkg / name)
            subject[name[:-3]] = sha256(src)
    elif kind != "panel":
        rng = f"{args.base}..{args.head}"
        for name, cmd in (("commits.txt", ["log", "--oneline", rng]), ("stat.txt", ["diff", "--stat", rng]),
                          ("diff.patch", ["diff", "--no-color", "--no-ext-diff", rng])):
            r = subprocess.run(["git", *cmd], cwd=str(primary), capture_output=True, creationflags=NO_WINDOW)
            if r.returncode:
                raise Exit(64, f"git {cmd[0]} {rng} failed: {r.stderr.decode('utf-8', 'replace')[-200:]}")
            (pkg / name).write_bytes(r.stdout)
    for dst, src in ev:
        dst.parent.mkdir(exist_ok=True)
        shutil.copyfile(src, dst)
    return subject, warnings


# ---------------------------------------------------------------- worktrees

def worktree_path(cfg, primary, feature_rel, kind, lane):
    name = f"{primary.name}-{feature_rel.replace('/', '-')}-{kind}-{lane}"
    return resolve_under(primary, cfg["worktrees"]) / "_review" / name


def tree_writes(path):
    """git status with ignored and untracked entries, less the package: any entry IS a write."""
    out = git_out(["status", "--porcelain", "--ignored", "--untracked-files=all"], path)
    return [l for l in out.splitlines() if l.strip() and not l[3:].lstrip('"').startswith(".parsec/")]


def ensure_worktree(primary, path, head):
    listed = [p.resolve() for p in worktree_list(primary)]
    if path.exists() and path.resolve() in listed:
        git_out(["checkout", "--detach", "--force", head], path)
        if tree_writes(path):                    # old item 98: a reused tree carried leftovers into every later round
            remove_worktree(primary, path)
        else:
            return
    git(["worktree", "prune"], primary)
    path.parent.mkdir(parents=True, exist_ok=True)
    git_out(["worktree", "add", "--detach", str(path), head], primary)


def unlink_links(top):
    """Links are removed as links, never walked into (2026-09-13: a recursive delete followed one out)."""
    os.chmod(top, 0o777)
    for e in os.scandir(top):
        if e.is_symlink() or e.is_junction():
            os.unlink(e.path)
        elif e.is_dir(follow_symlinks=False):
            os.chmod(e.path, 0o777)
            unlink_links(e.path)
        else:
            os.chmod(e.path, 0o666)


def remove_worktree(primary, path):
    path = Path(path)
    if is_link(path):
        raise Exit(64, f"{path} is a link; refused before anything was scanned")
    if not path.is_dir():
        raise Exit(64, f"{path} is not a directory")
    listed = [p.resolve() for p in worktree_list(primary)]
    if path.resolve() not in listed[1:]:        # old item 107: a removal tool handed the wrong path removes it
        raise Exit(64, f"{path} is not a non-primary worktree of {primary}")
    unlink_links(path)
    try:
        shutil.rmtree(path)                      # our own delete, so a held handle leaves the tree LISTED for a retry
    except OSError as e:
        raise Exit(1, f"{path}: a file is held open or undeletable ({e.filename}); the tree is left in place")
    git(["worktree", "prune"], primary)


# ---------------------------------------------------------------- launching a CLI

def last_write_age(paths):
    ages = []
    for p in filter(None, paths):
        try:
            ages.append(time.time() - os.stat(p).st_mtime)
        except OSError:
            pass
    return f"{int(min(ages))} s ago" if ages else "no file yet"


def kill_tree(p):
    """Old item 71: end the child FIRST while alive, so cmd.exe, node and the CLI do not outlive it."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True, creationflags=NO_WINDOW)
    else:
        p.kill()
    p.wait()


def run_child(argv, cwd, env, stdin, out_path, err_path, watch):
    """Returns (exit code or None on the cap, seconds). Prints only the 'still running' lines, flushed."""
    start, said = time.time(), set()
    with open(stdin or os.devnull, "rb") as fin, open(out_path, "wb") as fout, \
            (fout if err_path == out_path else open(err_path, "wb")) as ferr:
        p = subprocess.Popen(argv, cwd=str(cwd), env=env, stdin=fin, stdout=fout, stderr=ferr, creationflags=NO_WINDOW)
        while p.poll() is None:
            elapsed = time.time() - start
            if elapsed >= CAP_SECONDS:
                kill_tree(p)
                return None, int(time.time() - start)
            for m in STILL_MINUTES:
                if elapsed >= m * 60 and m not in said:
                    said.add(m)
                    print(f"still running: {int(elapsed // 60)} min, last write {last_write_age(watch())}", flush=True)
            time.sleep(min(POLL_SECONDS, 1.0))      # the child's exit is noticed within a second
    return p.returncode, int(time.time() - start)


def program(row):
    prog = shutil.which(row["command"][0])       # CreateProcess does not apply PATHEXT; codex is codex.CMD
    if not prog:
        raise Exit(64, f"{row['command'][0]} not found on PATH")
    return prog


def codex_argv(row, tier, reply, session):
    argv = [program(row), *row["command"][1:], *CODEX_FLAGS, "-m", row["model"], "-c", f"model_reasoning_effort={row['effort']}",
            "-c", f"service_tier={tier}",       # 2026-09-22: every round one night inherited the desktop app's Fast toggle
            "--output-last-message", str(reply)]
    return argv + (["resume", session, "-"] if session else ["-"])    # flags BEFORE resume (codex 0.153.4); never --last


def kimi_argv(row, session, empty):
    empty.mkdir(parents=True, exist_ok=True)     # old item 17: a canary skill loaded without --skills-dir
    argv = [program(row), *row["command"][1:], "-m", row["model"]]
    if session:
        argv += ["--session", session]           # exactly the token printed after -r, prefix included (owed 11)
    else:
        argv += ["--agent-file", str(PLUGIN / "lanes" / "kimi-reviewer.md")]   # the lane's only read-only control
    return argv + ["--skills-dir", str(empty), "--output-format", "text",
                   "-p", "Read the file .parsec/brief.md and follow it exactly."]


def codex_session_file(session):
    hits = list((Path.home() / ".codex" / "sessions").rglob(f"*{session}*.jsonl")) if session else []
    return hits[0] if hits else None


def kimi_session_file(home, tree_name):
    root = Path(home) / "sessions"
    cands = [p for p in root.glob(f"wd_{tree_name}_*/session_*/agents/main/wire.jsonl")] if root.is_dir() else []
    return max(cands, key=lambda p: p.stat().st_mtime) if cands else None


def session_of(lane, transcript_text):
    if lane == "kimi":
        m = re.findall(r"kimi -r (session_[0-9a-f-]+)", transcript_text)   # printed only when the round ends
        return m[-1] if m else None
    m = re.search(r"session id:\s*([0-9a-f-]{36})", transcript_text)       # the header, before the first token
    return m.group(1) if m else None


def tier_readback(session):
    """codex writes thread_settings_applied only on a resume; an unknown tier value is accepted silently."""
    f = codex_session_file(session)
    if not f:
        return None
    hits = re.findall(r'"service_tier":("[^"]*"|null)', read_text(f))
    return hits[-1].strip('"') if hits else None


# ---------------------------------------------------------------- rounds

def pretty_name(lane, kind, n):
    if kind == "prereview":
        return "Opus Pre-Review"
    if kind == "lastlook":
        return f"{lane.capitalize()} Last Look"    # 2026-09-22: five Opus last looks were labelled Fable
    return f"{lane.capitalize()} R{n} {kind.capitalize()} Round"


def prepare(args, launch):
    primary = primary_of(args.repo)
    cfg = load_config(primary)
    args.lane = args.lane or cfg.get("reviewer", {}).get("codex_lane", "sol")   # the config's lane when none is named (2026-09-22 review)
    if args.lane not in (CLI_LANES if launch else tuple(AGENT_OF)):
        raise Exit(64, f"lane {args.lane} (from the config's codex_lane) is not a lane")   # r3, r4: before anything is written, a panel folder included
    fdir, frel = feature_dir(cfg, primary, args.feature, args.round)
    if args.kind in ("prereview", "diff", "lastlook") and not args.base:
        raise Exit(64, f"--base is required for {args.kind}")
    if not args.head:                            # 2026-09-22 16:45: two panel rounds died in the parser wanting a range a panel has not
        if args.kind != "panel":
            raise Exit(64, f"--head is required for {args.kind}")
        args.head = git_out(["rev-parse", "--short", "HEAD"], primary).strip()
    if not Path(args.brief).is_file():
        raise Exit(64, f"brief not found: {args.brief}")
    folder = round_folder(fdir, args.kind, args.round, args.lane)
    files = [Path(f).resolve() for f in args.file or []]   # inside the round folder, the rerun's rename would move it away mid-round (2026-09-23, Sol)
    if len(set(files)) < len(files) or not all(f.is_file() and not f.is_relative_to(folder) for f in files):   # these three before any write (2026-09-23 pre-review: a new panel's folder was left behind)
        raise Exit(64, f"--file {' '.join(args.file)}: missing, given twice, or inside {folder.name}")
    for c in filter(None, (args.base, args.head)):
        git_out(["rev-parse", "--verify", f"{c}^{{commit}}"], primary)
    if args.kind == "design" and not all((fdir / n).is_file() for n in ("spec.md", "tasks.md")):
        raise Exit(64, f"design round without spec.md and tasks.md in {fdir}")
    cli = args.lane in CLI_LANES
    if cli:
        program(row := lane_row(args.lane))      # before anything is written (2026-09-23 last look: a new panel's folder was)
    warnings = []
    if args.round > 5:
        warnings.append(f"{args.lane}'s {args.kind} round {args.round}: past five rounds of one lane and kind the skill asks Brandon (old item 24)")
    if folder.exists() and not (folder / "record.json").is_file() and (folder / "pending.json").is_file():   # before the number check: an uncollected old-style round named round 1 (Kimi r2)
        raise Exit(64, f"{folder} was never collected: run round collect first")
    mine = [r for r in records(fdir) if (r.get("kind"), r.get("lane")) == (args.kind, args.lane)]
    nxt = 1 + max((r["round"] for r in mine if r.get("verdict") in VERDICTS), default=0)
    if args.round != nxt and not (mine and mine[-1].get("round") == args.round and mine[-1].get("verdict") not in VERDICTS):   # r1 (Sol): an old-style round with no verdict reruns under its number
        raise Exit(64, f"round {args.round}: {args.lane}'s next {args.kind} round is {nxt}; each lane counts its own rounds of a kind from 1, and a round with no verdict reruns under its number")   # 2026-09-22 KitnEssentials: a first diff round ran as r3 after design r1 and prereview r2
    if folder.exists():
        dead_rename(folder)
    session = None
    if not args.fresh and mine:
        session = mine[-1].get("session")
        session = None if session in (None, "", "unknown") else session
        if not session:
            warnings.append("newest record of this lane has no session id: fresh round")
    if not fdir.is_dir():                        # a new panel, round 1 (feature_dir): the one feature folder the tool makes
        fdir.mkdir(parents=True)
        (fdir / "ledger.md").write_text(f"# Panel {fdir.name}\n\nMade by parsec on {stamp()}.\n", encoding="utf-8", newline="\n")
    folder.mkdir(parents=True)
    shutil.copyfile(args.brief, folder / "brief.md")
    tree = worktree_path(cfg, primary, frel, args.kind, args.lane)   # every lane reads the code at --head (2026-09-23: seven phases gave Opus and Fable the primary)
    ensure_worktree(primary, tree, args.head)
    if cli:
        model, effort, agent = row["model"], row.get("effort", "lane home"), None
        subject, w = write_package(tree, args, cfg, primary, fdir, args.kind)
        if args.kind == "design":
            for name in ("spec.md", "tasks.md"):
                shutil.copyfile(fdir / name, folder / name)
    else:
        model, effort, agent = agent_seat(args.lane)
        subject, w = write_package(folder, args, cfg, primary, fdir, args.kind)
    warnings += w
    pending = {"kind": args.kind, "round": args.round, "lane": args.lane, "head": args.head, "base": args.base,
               "start": stamp(), "brief_sha256": sha256(args.brief), "tier": "fast" if args.fast else "default",
               "model": model, "effort": effort, "agent": agent, "resumed": bool(session), "session": session,
               "subject": subject, "worktree": str(tree), "feature": frel, "warnings": warnings}
    write_json(folder / "pending.json", pending)
    if not launch:
        print(f"task name: {pretty_name(args.lane, args.kind, args.round)}")
        print(f"brief: {folder / '.parsec' / 'brief.md'}")   # 2026-09-23: four phases hunted for the package
        print(f"code root: {tree} at {args.head}, a review worktree that round close removes")
        patch = folder / ".parsec" / "diff.patch"
        if patch.is_file():
            print(f"diff.patch: {len(read_text(patch).splitlines())} lines (Read pages 2,000 at a time)")
        print(f"report path: {folder / 'reply.md'}")
        for wl in warnings:
            print(f"warning: {wl}")
        return 0
    return run_round(args, primary, fdir, folder, pending, tree)


def run_round(args, primary, fdir, folder, pending, tree):
    row = lane_row(args.lane)
    reply, transcript = folder / "reply.md", folder / "transcript.log"
    session = pending["session"]
    if args.lane == "kimi":
        argv = kimi_argv(row, session, tree.parent / "_empty-skills")
        env = dict(child_env(), KIMI_CODE_HOME=str(resolve_under(PLUGIN, row["home"])))
        out, err, stdin = reply, transcript, None
        watch = lambda: [transcript, reply, kimi_session_file(env["KIMI_CODE_HOME"], tree.name)]
    else:
        argv = codex_argv(row, "priority" if args.fast else "default", reply.resolve(), session)
        env = child_env()
        out, err, stdin = transcript, transcript, folder / "brief.md"   # stdin is the file itself, never a pipe
        watch = lambda: [transcript, reply, codex_session_file(session or session_of("codex", read_text(transcript)))]
    code, secs = run_child(argv, tree, env, stdin, out, err, watch)
    return collect(args.repo, args.feature, args.kind, args.round, args.lane,
                   run={"cli_exit": code, "seconds": secs, "timeout": code is None})


def collect(repo, feature, kind, n, lane, degraded=None, close_minor=None, run=None):
    primary = primary_of(repo)
    cfg = load_config(primary)
    fdir, _ = feature_dir(cfg, primary, feature)
    folder = round_folder(fdir, kind, n, lane)
    rec_path, pend_path = folder / "record.json", folder / "pending.json"
    warnings = []
    if rec_path.is_file() and (degraded or close_minor):
        rec = read_json(rec_path)
        if degraded:
            rec["degraded"] = degraded
        if close_minor:
            if rec.get("verdict") != "FIX":
                raise Exit(64, f"--close-minor needs a FIX round; this one is {rec.get('verdict')}")
            rec["closed_on_minor"] = close_minor
        write_json(rec_path, rec)
        ledger_line(fdir, f"{kind} r{n} {lane}: " + (f"degraded ({degraded})" if degraded else f"FIX closed on Minor ({close_minor})"),
                    warnings)
        print(f"{pretty_name(lane, kind, n)}: record updated" + "".join(f"\nwarning: {w}" for w in warnings))
        return 0
    if not pend_path.is_file():                  # 2026-09-23: a collect after round run read as an error
        raise Exit(64, f"{folder.name} is already collected (round run collects its own round)" if rec_path.is_file() else f"nothing pending in {folder}")
    pend = read_json(pend_path)
    warnings += pend.get("warnings", [])
    reply = folder / "reply.md"
    text = read_text(reply) if reply.is_file() else ""
    transcript = read_text(folder / "transcript.log") if (folder / "transcript.log").is_file() else ""
    verdict = verdict_of(text)
    continuity = tag_line(text, "CONTINUITY") if pend.get("resumed") else None
    session = pend.get("session") or session_of(lane, transcript) or "unknown"
    cli_version = (re.search(r"OpenAI Codex v(\S+)", transcript) or [None, "unknown"])[1] if lane != "kimi" else "unknown"
    clean = None
    if pend.get("worktree") and not Path(pend["worktree"]).is_dir():   # 2026-09-22 review: a removed tree left the round unfinalisable;
        verdict, warnings = "NONE", warnings + ["worktree missing: no clean-tree evidence, so no verdict"]   # r2 (Sol): and no PASS without it
    elif pend.get("worktree"):
        writes = tree_writes(Path(pend["worktree"]))
        clean = not writes
        if writes:
            verdict = "WROTE-FILES"               # replaces the verdict: a PASS from a reviewer that wrote never counts
            warnings.append("reviewer wrote files: " + "; ".join(writes[:5]))
    tier, check = pend.get("tier", "default"), "unverified"
    if lane in ("astra", "sol") and pend.get("resumed") and session != "unknown":
        read = tier_readback(session)
        if read is None:
            warnings.append("tier read-back: no thread_settings_applied record found")
        elif read == ("priority" if tier == "fast" else "default"):
            check = "verified"
        else:
            warnings.append(f"tier read-back {read} differs from the requested {tier}")
            tier, check = read, "unrequested"
    run = run or {"cli_exit": None, "seconds": None, "timeout": False}
    if run["timeout"]:
        verdict = "NONE"
        warnings.append("TIMEOUT: the cap ended the round")
    if kind == "lastlook" and lane != "fable":    # 2026-09-23: six Opus stand-ins were recorded as a plain PASS
        degraded = degraded or f"stand-in last look on {lane}; a Fable last look on the same head supersedes it"
    end = now()
    rec = {**{k: v for k, v in pend.items() if k not in ("warnings",)}, "cli_version": cli_version, "session": session,
           "continuity": continuity, "end": stamp(end), "seconds": run["seconds"], "cli_exit": run["cli_exit"],
           "verdict": verdict, "clean_tree": clean, "tier": tier, "tier_check": check, "degraded": degraded,
           "closed_on_minor": None, "reply": str(reply), "warnings": warnings}
    write_json(rec_path, rec)
    pend_path.unlink()                           # before the ledger line: the record is the truth, a replay would overwrite it (r2, Sol)
    cont = "" if continuity is None and not pend.get("resumed") else (", continuity answered" if continuity else ", continuity: not answered")
    ledger_line(fdir, f"{kind} r{n} {lane}: {verdict}{cont}" + (", tier: fast" if tier == "fast" else "")
                + (f", degraded ({degraded})" if degraded else "") + f", rounds\\{folder.name}\\reply.md", warnings)
    sub = "  ".join(f"{k} {v[:6]}" for k, v in pend.get("subject", {}).items())
    print(f"{pretty_name(lane, kind, n)}\nverdict: {verdict}    " + ("in-session agent" if lane in AGENT_OF else f"cli exit: {run['cli_exit']}    {run['seconds']} s    "
          f"{'resumed' if pend.get('resumed') else 'fresh'} session {session}    tier {tier}") + (f"\ndegraded: {degraded}" if degraded else ""))
    print(f"repo:    {primary}    head {pend.get('head')}\nreply:   {reply}" + (f"\nsubject: {sub}" if sub else ""))
    for w in warnings:
        print(f"warning: {w}")
    code = 67 if run["timeout"] else 66 if verdict == "WROTE-FILES" else 65 if verdict == "NONE" else (run["cli_exit"] or 0)
    if code and transcript:
        print("transcript tail:\n" + "\n".join(transcript.splitlines()[-5:]))
    return code


def close_rounds(args):
    primary = primary_of(args.repo)
    cfg = load_config(primary)
    _, frel = feature_dir(cfg, primary, args.feature)
    pat = re.compile(re.escape(f"{primary.name}-{frel.replace('/', '-')}-") + f"({args.kind or '|'.join(KINDS)})-({'|'.join(CLI_LANES + tuple(AGENT_OF))})")
    review = resolve_under(primary, cfg["worktrees"]) / "_review"
    n = 0
    for p in sorted(review.iterdir()) if review.is_dir() else []:
        if pat.fullmatch(p.name) and p.is_dir():     # anchored: 09-22-x must not close 09-22-x-more (2026-09-22 review)
            remove_worktree(primary, p)
            print(f"removed {p}")
            n += 1
    print(f"{n} review worktree(s) removed")
    return 0


# ---------------------------------------------------------------- verify, task-brief, build

def verify(args):
    primary = primary_of(args.repo)
    cfg = load_config(primary)
    fdir, _ = feature_dir(cfg, primary, args.feature)
    have = {n: sha256(fdir / f"{n}.md") if (fdir / f"{n}.md").is_file() else None for n in ("spec", "tasks")}
    design = [r for r in records(fdir) if r.get("kind") == "design" or "reason" in r]
    newest = design[-1] if design else None
    warnings = []

    def stands(r):   # a PASS, a FIX closed on Minor, or an amendment
        return r is not None and ("reason" in r or r.get("verdict") == "PASS" or
                                  (r.get("verdict") == "FIX" and r.get("closed_on_minor")))
    if args.record_amendment:
        if not stands(newest):                    # Screenshot 1: a task list edited after its PASS
            raise Exit(64, "amendment refused: the newest design record is not a PASS, a FIX closed on Minor, or an amendment")
        k = 1 + len([r for r in design if "reason" in r])
        write_json(fdir / "rounds" / f"amendment-{k}.json",
                   {"time": stamp(), "reason": args.record_amendment, "subject": have, "degraded": newest.get("degraded")})
        ledger_line(fdir, f"amendment {k}: {args.record_amendment}", warnings)
        print(f"amendment {k} recorded: spec {have['spec'][:8]}  tasks {have['tasks'][:8]}")
        return 0
    if not stands(newest):
        print("NO-PASS-YET")
        return 0
    status = "MATCH" if newest.get("subject") == have else "CHANGED"
    if status == "MATCH" and "reason" not in newest and newest.get("closed_on_minor"):
        status += " (CLOSED ON MINOR)"
    elif status == "MATCH" and newest.get("degraded"):
        status += " (DEGRADED PASS)"
    print(status)
    return 0


def sections(text):
    """(heading, bytes-span) for each `## ` section; the header is what comes before the first."""
    marks = [m.start() for m in re.finditer(rb"(?m)^## ", text)] + [len(text)]
    return [(text[a:text.find(b"\n", a)].decode("utf-8", "replace").strip(), text[a:b]) for a, b in zip(marks, marks[1:])], text[:marks[0]]


def task_brief(args):
    primary = primary_of(args.repo)
    cfg = load_config(primary)
    fdir, _ = feature_dir(cfg, primary, args.feature)
    text = (fdir / "tasks.md").read_bytes()
    secs, header = sections(text)
    consts = [b for h, b in secs if h.lower().startswith("## global constraints")]
    task = [b for h, b in secs if re.match(rf"## Task {args.task}\b", h)]
    if not task:
        raise Exit(64, f"tasks.md has no `## Task {args.task}` section")
    (fdir / "build").mkdir(exist_ok=True)
    out = fdir / "build" / f"task-{args.task:02d}-brief.md"
    out.write_bytes(header + b"".join(consts) + task[0])                 # old item 113: the slice IS the bytes
    print(f"{out}\n{sha256(out)}")
    return 0


def archive_task(fdir, n):
    report, log = fdir / "build" / f"task-{n:02d}-report.md", fdir / "build" / f"task-{n:02d}-agy.log"
    if report.is_file():
        k = dead_rename(report)
        if log.is_file():
            log.rename(log.with_name(f"{log.name}.dead{k}"))
        return k
    return 0


def build_run(args):
    primary = primary_of(args.repo)
    cfg = load_config(primary)
    fdir, _ = feature_dir(cfg, primary, args.feature)
    brief = fdir / "build" / f"task-{args.task:02d}-brief.md"
    report, log = fdir / "build" / f"task-{args.task:02d}-report.md", fdir / "build" / f"task-{args.task:02d}-agy.log"
    checkout = Path(args.checkout)
    if not brief.is_file() or not checkout.is_dir():
        raise Exit(64, f"need {brief} and the checkout {checkout}")
    at = git_out(["rev-parse", "HEAD"], checkout).strip()
    if not args.head or not (at.startswith(args.head) or args.head.startswith(at)):   # 2026-09-22 17:23: Gemini built on a tree the brief told it to refuse
        raise Exit(64, f"{checkout} is at {at[:8]}, not --head {args.head}: the lane never checks, so the tool does")
    docs = resolve_under(primary, cfg["docs_root"])   # r2 to r4 (Sol, Opus): the docs root inside the tree is the plugin's, never dirt; the whole tree never is
    rel = next((docs.relative_to(r.resolve()).as_posix() for r in (checkout, primary) if docs.is_relative_to(r.resolve()) and docs != r.resolve()), None)
    dirt = lambda: [l for l in git_out(["status", "--porcelain", "--untracked-files=all"], checkout).splitlines() if l.strip() and not (rel and re.match(rf'"?{re.escape(rel)}/', l[3:]))]
    if dirt():                                   # 2026-09-22 review (Sol): a leftover made the status test vacuous
        raise Exit(64, f"{checkout} is dirty before the build; the success test reads git status, so it must start clean")
    eol_before = eol_map(checkout)
    if report.is_file():
        if not args.again:
            raise Exit(64, f"{report} exists: --again archives it first")
        archive_task(fdir, args.task)
    row = lane_row("gemini")
    prog = program(row)                          # missing: every task goes to the backup implementer
    digest = sha256(brief)
    copy = checkout / f"AGY-TASK-BRIEF-{digest[:12]}.md"
    warnings, lines = [], []
    try:
        shutil.copyfile(brief, copy)
        if sha256(copy) != digest:
            raise Exit(64, "the brief copy does not match the brief")
        prompt = f"Read the file {copy.name} in the workspace and make its file edits exactly. {CLOSING}"
        argv = [prog, *row["command"][1:], "-p", prompt, "--model", row["model"], "--mode", "accept-edits",
                "--add-dir", str(checkout), "--log-file", str(log.resolve())]   # 2026-09-13: a /c/ path made no log
        env = dict(child_env(), AGY_CLI_DISABLE_AUTO_UPDATE="true")    # old item 112: the literal true
        code, secs = run_child(argv, checkout, env, None, report, fdir / "build" / f"task-{args.task:02d}-agy.err", lambda: [log, report])
    finally:
        if copy.exists():
            copy.unlink()                        # 2026-09-22 03:07: git status mid-run listed the copy
    err = fdir / "build" / f"task-{args.task:02d}-agy.err"
    err_text = read_text(err) if err.is_file() else ""
    err.unlink(missing_ok=True)
    log_text = read_text(log) if log.is_file() else ""
    message = read_text(report).strip()
    status = "\n".join(dirt())
    checks = [(f"route line present: {r}", r in log_text) for r in ROUTE_LINES]
    checks += [("no soft-denied step", SOFT_DENY not in log_text), ("final message non-empty", bool(message)),
               ("git status non-empty (an empty diff is never done)", bool(status)),
               ("line endings kept on every modified file", all(eol_before.get(p, w) in (w, "w/none", "w/") or w in ("w/none", "w/") for p, w in eol_map(checkout).items() if not (rel and p.startswith(rel + "/")))),   # r2 (Sol): no ending yet, or a file gone, is nothing to flip; r4: nor the docs root
               ("finished within the cap", code is not None)]   # 2026-09-22 review: a capped run failed with no named reason
    ok = all(c for _, c in checks)
    lines = ["", "---", f"parsec build run: task {args.task:02d}, lane gemini, model {row['model']}, {secs} s, "
             f"agy exit {code} (recorded, never trusted)"] + [f"- {'ok' if c else 'FAILED'}: {n}" for n, c in checks]
    lines += [f"- result: {'ok' if ok else 'failed'}"] + ([f"- agy stderr tail: {err_text.strip().splitlines()[-1][:200]}"] if err_text.strip() else [])
    with open(report, "a", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    ledger_line(fdir, f"build task {args.task:02d} gemini: {'ok' if ok else 'failed'}, build\\{report.name}", warnings)
    print(f"Task {args.task} Implement\n" + "\n".join(lines[2:]) + "".join(f"\nwarning: {w}" for w in warnings))
    return 0 if ok else 65


def eol_map(checkout):                            # 2026-09-22 02:06: LF written into CRLF files, tests green, diff unreadable; the
    out = git_out(["ls-files", "--eol", "-z"], checkout)   # r3: through git_out, so a failed call never passes the check
    return {e.split("\t", 1)[1]: e.split()[1] for e in out.split("\0") if "\t" in e}   # w/ token before vs after (18:20: the HEAD blob misreads autocrlf)


def build_archive(args):
    primary = primary_of(args.repo)
    cfg = load_config(primary)
    fdir, _ = feature_dir(cfg, primary, args.feature)
    k = archive_task(fdir, args.task)
    print(f"task {args.task:02d}: " + (f"report and log renamed .dead{k}" if k else "no report to archive"))
    return 0


# ---------------------------------------------------------------- doctor

def probe(argv, env=None, timeout=10, stdin_text=None):
    """One CLI call with a 10-second timeout: a version call can start an updater."""
    prog = shutil.which(argv[0])
    if not prog:
        return None, f"{argv[0]} not found on PATH"
    try:
        r = subprocess.run([prog, *argv[1:]], capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, env=env, input=stdin_text, creationflags=NO_WINDOW)
        return r.returncode, (r.stdout + r.stderr).strip().splitlines()[0] if (r.stdout + r.stderr).strip() else ""
    except subprocess.TimeoutExpired:
        return None, "timed out after 10 s"


def codex_quota(cmd):
    """The free quota read (codex app-server, account/rateLimits/read), information only: never fails a pre-flight."""
    p, found = None, []
    try:
        req = json.dumps({"id": 1, "method": "initialize", "params": {"clientInfo": {"name": "parsec-doctor", "version": "0"},
                          "capabilities": {"experimentalApi": True}}}) + "\n" + \
              json.dumps({"id": 2, "method": "account/rateLimits/read", "params": None}) + "\n"
        p = subprocess.Popen([shutil.which(cmd[0]), *cmd[1:], "app-server", "--stdio"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, env=child_env(), creationflags=NO_WINDOW)
        p.stdin.write(req.encode("utf-8"))
        p.stdin.flush()                          # stdin stays OPEN: the server exits when it closes
        t = threading.Thread(target=lambda: found.append(next((l for l in iter(p.stdout.readline, b"") if b"rateLimits" in l), b"")), daemon=True)
        t.start(); t.join(10)                    # 2026-09-22 review: a readline on a silent server had no deadline at all
        if found and found[0]:
            lim = json.loads(found[0]).get("result", {}).get("rateLimits", {})
            parts = [f"{'5 h' if (w.get('windowDurationMins') or 0) <= 300 else 'week'} {100 - w.get('usedPercent', 0)}% left"
                     for w in (lim.get("primary"), lim.get("secondary")) if w]
            return "quota: " + ", ".join(parts) if parts else "quota: no windows in the answer"
    except (ValueError, OSError):
        pass
    finally:
        if p:
            kill_tree(p)                         # on every path, a broken pipe included; the tree, since codex is a .CMD (2026-09-22 review, r2)
    return "quota: unavailable"


def preflight(args):
    primary = primary_of(args.repo)
    cfg = load_config(primary)
    lines, fail = [], []
    row = lane_row(args.lane) if args.lane in lanes() else None
    cmd = list(row["command"]) if row else []
    if args.lane in ("astra", "sol"):
        code, ver = probe(cmd + ["--version"])
        if code != 0:
            fail.append(f"codex: {ver}")
        code, login = probe(cmd + ["login", "status"], env=child_env())
        if code != 0 or "not logged in" in login.lower():
            fail.append(f"login: {login or 'no answer'}")
        lines.append(f"- **CLI:** {ver}, {login}")
        lines.append(f"- **Quota:** {(codex_quota(cmd) if code == 0 else 'quota: not read').removeprefix('quota: ')}")
        lines.append(f"- **Model:** {row['model']}, effort {row['effort']} (lanes.toml), {'fast' if args.fast else 'fast off'}")
    elif args.lane == "kimi":
        code, ver = probe(cmd + ["--version"])
        if code != 0:
            fail.append(f"kimi: {ver}")
        home = resolve_under(PLUGIN, row["home"])
        conf = read_text(home / "config.toml") if (home / "config.toml").is_file() else ""
        alias, effort = f'[models."{row["model"]}"]' in conf, "default_effort" in conf
        if not alias:
            fail.append(f"model {row['model']} is not in the lane home's config")
        lines.append(f"- **CLI:** kimi {ver}")
        lines.append(f"- **Lane home:** {home}, model alias {'present' if alias else 'MISSING'}, "
                     f"default_effort {'present' if effort else 'MISSING'} (effort lives in the lane home)")
    elif args.lane == "gemini":
        code, ver = probe(cmd + ["--version"])
        if code != 0:
            fail.append(f"agy: {ver}")
        lines.append(f"- **CLI:** agy {ver} at {shutil.which(cmd[0])}")
        lines.append(f"- **Model:** {row['model']} (lanes.toml); login is read from the first run's log")
    elif args.lane in AGENT_OF:
        model, effort, agent = agent_seat(args.lane)
        lines.append(f"- **Agent:** {agent}, model {model}, effort {effort} (agent file)")
    else:
        raise Exit(64, f"lane {args.lane} is not a lane or a seat")   # 2026-09-22 review: a typo raised KeyError
    if args.feature:
        try:
            feature_dir(cfg, primary, args.feature, 1)   # 2026-09-23: doctor accepted a --feature that round run then refused
        except Exit as e:
            fail.append(str(e))
    if args.kind != "build":
        _, warnings, found, wanted = context_lines(cfg, primary, None)
        fail += [w for w in warnings if "not found" in w]
        files = len([c for c in cfg.get("context", []) if c.get("role", "rubric") == "rubric"])
        rub = f"rubric {files} file{"s" * (files != 1)}, {found} of {wanted} sections found" if files else "rubric none configured"   # r3: a rubric without sections is still a rubric
        wt = resolve_under(primary, cfg["worktrees"])
        lines.append(f"- **Checks:** {rub} · worktrees folder {'ok' if wt.is_dir() else 'MISSING: ' + str(wt)}")
        if not wt.is_dir():
            fail.append("worktrees folder missing")
    title = f"Pre-flight: {args.lane.capitalize()} · {args.kind}" + (" debate" if args.kind != "build" else "")   # Markdown, posted as is (Brandon, 2026-09-23)
    print(f"### 🔴 {title} · FAILED\n\n**{'; '.join(fail)}**" if fail else f"### 🟢 {title}")
    print((f"\n**{args.feature}**\n" if args.feature else "") + "\n" + "\n".join(lines))
    return 64 if fail else 0


def doctor(args):
    if args.lane:
        return preflight(args)
    rows, review, wt, bad, out = lanes(), None, None, False, []
    try:
        primary = primary_of(args.repo)
        cfg = load_config(primary)
        wt = resolve_under(primary, cfg["worktrees"])
        review = wt / "_review"
    except Exit as e:
        out.append(f"- 🔴 **config:** {e}"); bad = True   # the table still prints, the exit says setup is owed (2026-09-22 review)
    mkt, entry = installed_entry()
    known = Path.home() / ".claude" / "plugins" / "known_marketplaces.json"   # 2026-09-23: the cached copy is no git checkout, so /parsec:doctor always said STALE
    src = read_json(known).get(mkt, {}).get("installLocation") if mkt and known.is_file() else None
    head = git(["rev-parse", "HEAD"], src if src and Path(src).is_dir() else PLUGIN).stdout.strip() or "unknown"
    sha, ok = entry.get("gitCommitSha", ""), entry.get("gitCommitSha") == head
    out.insert(0, f"- {'🟢' if ok else '🔴'} **plugin install:** " + (f"{entry.get('version')} at {sha[:8]}: " + ("ok" if ok else f"STALE (repo head {head[:8]}; the cache is keyed by version: bump it, then claude plugin update)") if entry else "not installed"))   # old item 65; 2026-09-22 17:16
    for name, row in rows.items():
        code, ver = probe([row["command"][0], "--version"])
        login = probe(row["command"] + ["login", "status"], env=child_env())[1] if name in ("astra", "sol") else "login: the first run's log" \
            if name == "gemini" else f"credentials {'present' if (resolve_under(PLUGIN, row['home']) / 'credentials').exists() else 'MISSING'} in the lane home"
        good = code == 0 and "not logged in" not in login.lower() and "MISSING" not in login
        out.append(f"- {'🟢' if good else '🔴'} **lane {name}:** {row['model']}, effort {row.get('effort', 'lane home' if name == 'kimi' else 'the model')}, {ver}, {login}")
    for folder, label in ((wt, "worktrees"), (review, "_review")):
        if folder and folder.is_dir():
            for p in sorted(folder.iterdir()):
                if p.is_dir() and not p.name.startswith("_"):
                    out.append(f"- **{label}:** {p.name}, {int((time.time() - p.stat().st_mtime) / 86400)} d old")
    print(f"### {'🔴' if any('🔴' in l for l in out) else '🟢'} parsec doctor\n\n" + "\n".join(out))   # Markdown, posted as is (Brandon, 2026-09-23)
    if args.update:
        print("\nwarning: a debate may be open in another chat; its lane's update lands mid-debate\n")
        for upd, name in {tuple(r["update"]): ", ".join(m for m, s in rows.items() if s.get("update") == r["update"]) for r in rows.values() if r.get("update")}.items():   # one update per CLI, every lane named (2026-09-22 review, r3)
            code, msg = probe(list(upd), timeout=600, env=dict(os.environ, AGY_CLI_DISABLE_AUTO_UPDATE="true"))
            print(f"- **update {name}:** exit {code}, {msg}")
    return 64 if bad else 0


# ---------------------------------------------------------------- argparse and the one exit

def parser():
    p = argparse.ArgumentParser(prog="parsec", description="The debate round as a tool (plugin parsec).")
    p.add_argument("--repo", default=os.getcwd(), help="a checkout; the primary is found from it")
    sub = p.add_subparsers(dest="cmd", required=True)
    rnd = sub.add_parser("round", help="run, prepare, collect or close a review round").add_subparsers(dest="sub", required=True)
    for name, hint in (("run", "one round on a CLI lane (astra, sol, kimi)"), ("prepare", "the package for an in-session lane (opus, fable)")):
        q = rnd.add_parser(name, help=hint)
        q.add_argument("--feature", required=True, help="feature folder under the docs root")
        q.add_argument("--kind", required=True, choices=KINDS)
        q.add_argument("--round", required=True, type=int)
        q.add_argument("--lane", required=name == "prepare", choices=CLI_LANES if name == "run" else tuple(AGENT_OF), help="run: default the config's codex_lane")   # 2026-09-22 r2 (Sol): prepare without --lane packaged a codex round
        q.add_argument("--brief", required=True, help="written with a file tool; copied byte for byte")
        q.add_argument("--head", help="required except for a panel, which takes the primary's HEAD")
        q.add_argument("--base", help="prereview, diff, lastlook")
        q.add_argument("--file", action="append", help="evidence, copied as evidence/<k>-<basename>")
        q.add_argument("--reference", help="one reference-code subfolder")
        q.add_argument("--fresh", action="store_true", help="do not resume")
        q.add_argument("--fast", action="store_true", help="codex service_tier=priority, on Brandon's word only")
    q = rnd.add_parser("collect", help="finalise a pending round, or mark one degraded or closed on Minor")
    for a in ("--feature", "--kind", "--lane"):
        q.add_argument(a, required=True)
    q.add_argument("--round", required=True, type=int)
    q.add_argument("--degraded", metavar="REASON")
    q.add_argument("--close-minor", metavar="REASON")
    q = rnd.add_parser("close", help="remove the feature's review worktrees")
    q.add_argument("--feature", required=True)
    q.add_argument("--kind", choices=KINDS)       # 2026-09-22 r2 (Sol): a free string reached the name pattern
    q = sub.add_parser("verify", help="spec.md and tasks.md against the newest design record or amendment")
    q.add_argument("--feature", required=True)
    q.add_argument("--record-amendment", metavar="REASON")
    q = sub.add_parser("task-brief", help="slice task N into build/task-NN-brief.md")
    q.add_argument("--feature", required=True)
    q.add_argument("--task", required=True, type=int)
    bld = sub.add_parser("build", help="the implementer (the Gemini lane)").add_subparsers(dest="sub", required=True)
    q = bld.add_parser("run", help="run task N through agy in the checkout")
    q.add_argument("--feature", required=True)
    q.add_argument("--task", required=True, type=int)
    q.add_argument("--checkout", required=True)
    q.add_argument("--head", required=True, help="the commit the task builds on; refused when the checkout is elsewhere")
    q.add_argument("--again", action="store_true", help="archive the earlier report and log first")
    q = bld.add_parser("archive", help="rename task N's report and log .dead<k>")
    q.add_argument("--feature", required=True)
    q.add_argument("--task", required=True, type=int)
    q = sub.add_parser("remove-worktree", help="remove a review worktree, links first")
    q.add_argument("path")
    q = sub.add_parser("doctor", help="the table, one lane's pre-flight, or the updates")
    q.add_argument("--lane")
    q.add_argument("--kind", default="design")
    q.add_argument("--feature")
    for a in ("--fast", "--update"):
        q.add_argument(a, action="store_true")
    return p


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):     # 2026-08-11: em dashes as ??? (a test's StringIO has no reconfigure)
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    args = parser().parse_args(argv)
    if (late := behind()):
        print(f"warning: {late}")
    try:
        if args.cmd == "round" and args.sub in ("run", "prepare"):
            return prepare(args, launch=args.sub == "run")
        if args.cmd == "round" and args.sub == "collect":
            return collect(args.repo, args.feature, args.kind, args.round, args.lane, args.degraded, args.close_minor)
        if args.cmd == "round":
            return close_rounds(args)
        if args.cmd == "verify":
            return verify(args)
        if args.cmd == "task-brief":
            return task_brief(args)
        if args.cmd == "build":
            return build_run(args) if args.sub == "run" else build_archive(args)
        if args.cmd == "remove-worktree":
            remove_worktree(primary_of(args.repo), Path(args.path)); print(f"removed {args.path}")
            return 0
        return doctor(args)
    except Exit as e:
        print(f"error: {e}", flush=True)
        return e.code


if __name__ == "__main__":
    sys.exit(main())
