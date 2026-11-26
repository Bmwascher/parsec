"""Tests for tools/parsec.py, each standing on a recorded failure (step 5 of the rethink, rows 1 to 17).
The fake CLI is evals/tests/fake_cli.py; no model call, no network. Rows that need junctions or
taskkill run on Windows only."""
import importlib.util, json, os, pytest, shutil, stat, subprocess, sys, time, uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FAKE = Path(__file__).with_name("fake_cli.py")
spec = importlib.util.spec_from_file_location("parsec", REPO / "tools" / "parsec.py")
parsec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parsec)
WIN = os.name == "nt"
blk = lambda out: out[:out.rindex("\n\nnext: post the block above")] + "\n"   # the summary block, less the post line printed after it (field audit 4)
TRICKY = "em — dash, \"quotes\", it's, `tick`, back\\slash, $HOME, 100%\n\n\nthree blank lines above, LF only\n"


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def env(tmp_path, monkeypatch):
    """A primary repo with a config, a feature, a lanes file that names the fake, and a fake home."""
    home = tmp_path / "home"
    (home / ".codex" / "sessions" / "2026").mkdir(parents=True)
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("HOME", str(home))
    repo = tmp_path / "proj"
    repo.mkdir()
    git("init", "-q", "-b", "main", cwd=repo)
    git("config", "user.email", "t@example.invalid", cwd=repo)
    git("config", "user.name", "t", cwd=repo)
    (repo / "AGENTS.md").write_text("# Rules\n\n## Lua style\n\nx\n\n## Git\n\ny\n", encoding="utf-8")
    (repo / "code.txt").write_text("one\n", encoding="utf-8")
    (repo / ".gitignore").write_text("docs/\n.claude/\nignored.txt\n", encoding="utf-8")
    git("add", "AGENTS.md", "code.txt", ".gitignore", cwd=repo)
    git("commit", "-qm", "base", cwd=repo)
    base = git("rev-parse", "HEAD", cwd=repo)
    (repo / "code.txt").write_text("one\ntwo\n", encoding="utf-8")
    git("commit", "-qam", "head", cwd=repo)
    head = git("rev-parse", "HEAD", cwd=repo)
    wt = tmp_path / "wt"
    wt.mkdir()
    (repo / ".claude").mkdir()
    (repo / ".claude" / "parsec.toml").write_text(
        f'docs_root = "docs"\nworktrees = "{wt.as_posix()}"\n[[context]]\npath = "AGENTS.md"\nrole = "rubric"\n'
        'sections = ["Lua style", "Git"]\n', encoding="utf-8")
    feat = repo / "docs" / "09-22-x"
    feat.mkdir(parents=True)
    (feat / "spec.md").write_text("# Spec\n\nthe spec\n", encoding="utf-8")
    (feat / "ledger.md").write_text("# Ledger\n\n", encoding="utf-8")
    brief = tmp_path / "brief.md"
    brief.write_bytes(TRICKY.encode("utf-8"))
    lanes = tmp_path / "lanes.toml"
    cmd = json.dumps([sys.executable, str(FAKE)])
    lanes.write_text(f'[astra]\nmodel = "gpt-6-astra"\neffort = "high"\ncommand = {cmd}\n'
                     f'[sol]\nmodel = "gpt-5.6-sol"\neffort = "high"\ncommand = {cmd}\n'
                     f'[kimi]\nmodel = "kimi-code/k3"\ncommand = {cmd}\nhome = "{(tmp_path / "kimi-home").as_posix()}"\n'
                     f'[neon]\nmodel = "gemini-4-neon-high"\neffort = "high"\ncommand = {cmd}\n'
                     f'[muse]\nmodel = "muse-wonder-full-1.0"\neffort = "high"\ncommand = {cmd}\n', encoding="utf-8")
    (tmp_path / "kimi-home").mkdir()
    (tmp_path / "kimi-home" / "config.toml").write_text('[models."kimi-code/k3"]\ndefault_effort = "high"\n', encoding="utf-8")
    monkeypatch.setattr(parsec, "LANES_FILE", lanes)
    monkeypatch.setattr(parsec, "CLAUDE", [sys.executable, str(FAKE)])   # never the real claude, whose update would install
    monkeypatch.setattr(parsec, "CLAUDE_LATEST", None, raising=False)    # no lookup for Claude Code; raising=False lets the new doctor test run red on the base tool, and test_doctor_stale_install's exact Claude Code row catches a renamed constant
    monkeypatch.setattr(parsec, "POLL_SECONDS", 0.05)
    log = tmp_path / "calls.jsonl"
    monkeypatch.setenv("FAKE_LOG", str(log))
    monkeypatch.setenv("FAKE_STDOUT", "OpenAI Codex v9.9.9\n--------\nsession id: 01a0c9a2-0000-4000-8000-000000000001\n--------\n")
    monkeypatch.setenv("FAKE_REPLY", "Summary.\n\nVERDICT: FIX\n")
    for k in ("FAKE_EXIT", "FAKE_VERSION_EXIT", "FAKE_SLEEP", "FAKE_WRITE", "FAKE_STDERR", "FAKE_STDIN_COPY", "FAKE_ENV_DUMP", "FAKE_CHILD_PID_FILE", "CLAUDE_CODE_ENTRYPOINT"):   # FAKE_VERSION_EXIT: none from the runner's environment (Sol R5 F3, Astra F35)
        monkeypatch.delenv(k, raising=False)

    e = type("E", (), {})()
    e.tmp, e.repo, e.feat, e.brief, e.head, e.base, e.wt, e.home, e.log, e.mp = tmp_path, repo, feat, brief, head, base, wt, home, log, monkeypatch
    e.calls = lambda: [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
    e.ledger = lambda: (feat / "ledger.md").read_text(encoding="utf-8")
    e.record = lambda kind, n, lane: json.loads((feat / "rounds" / f"{kind}-r{n}-{lane}" / "record.json").read_text(encoding="utf-8"))
    return e


def run(e, *args, **kw):
    """The tool in-process; returns (exit code, printed text)."""
    argv = ["--repo", str(e.repo), *args]
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            code = parsec.main(argv)
        except SystemExit as ex:      # argparse
            code = ex.code
    return code, buf.getvalue()


def rnd(e, n=1, lane="astra", kind="design", *extra, **kw):
    args = ["round", "run", "--feature", "09-22-x", "--kind", kind, "--round", str(n), "--lane", lane,
            "--brief", str(e.brief), "--head", e.head, *extra]
    if kind != "design":
        args += ["--base", e.base]
    return run(e, *args)


# row 1: codex argument list, on round 1 and on resume; 2026-07-24, 07-28, 08-11, 09-22 (the inherited tier); row 3: CODEX_HOME is absent from the codex child (2026-07-24)
def test_codex_flags_before_resume(env):
    e = env
    e.mp.setenv("CODEX_HOME", str(e.tmp / "elsewhere"))
    e.mp.setenv("FAKE_ENV_DUMP", str(e.tmp / "env.json"))
    code, out = rnd(e, 1)
    assert code == 0 and "CODEX_HOME" not in (child := json.loads((e.tmp / "env.json").read_text(encoding="utf-8"))) and child["NO_COLOR"] == "1", out
    pairs = list(zip(fresh := e.calls()[-1], fresh[1:]))
    for flag in (("--sandbox", "read-only"), ("--disable", "plugins"), ("--disable", "apps"), ("--disable", "memories"),
                 ("-c", "mcp_servers.node_repl.enabled=false"), ("-c", "service_tier=default"), ("-m", "gpt-6-astra"),
                 ("-c", "model_reasoning_effort=high")):
        assert flag in pairs, (flag, fresh)
    assert fresh[-1] == "-" and "resume" not in fresh and "--last" not in fresh
    code, out = rnd(e, 2)
    resumed = e.calls()[-1]
    i = resumed.index("resume")
    assert resumed[i + 1] == "01a0c9a2-0000-4000-8000-000000000001" and resumed[i + 2] == "-"
    assert all(f in resumed[:i] for f in ("--sandbox", "--disable", "-m", "--output-last-message", "service_tier=default"))
    assert e.record("design", 2, "astra")["resumed"] is True
    code, out = rnd(e, 1, "sol", "design", "--fresh")
    assert "gpt-5.6-sol" in e.calls()[-1] and "resume" not in e.calls()[-1]
    assert "round run collects its own round" in run(e, "round", "collect", "--feature", "09-22-x", "--kind", "design", "--round", "1", "--lane", "sol")[1]   # 0.1.9 last look F2: kept for a CLI round
    ctx = (e.wt / "_review" / "proj-09-22-x-design-sol" / ".parsec" / "context.md").read_text(encoding="utf-8")
    assert ctx.splitlines()[2].startswith("- your lane, Sol: you may run read-only commands") and "(git show, git log, git grep; rg is not on this sandbox's PATH)" in ctx   # 2026-09-23 audit: a driver's command ban cost a Sol round; 2026-09-28: "not installed" read as a project fact


# row 2: the Kimi argument list and child environment (old item 17; the dead normal-home login, 2026-09-21)
def test_kimi_arguments_and_home(env):
    e = env
    e.mp.setenv("FAKE_STDOUT", "Summary.\n\nVERDICT: PASS\n")
    e.mp.setenv("FAKE_STDERR", "thinking...\nTo resume this session: kimi -r session_2fc45d80-9dc5-4b9b-9561-65f39c787383\n")
    e.mp.setenv("FAKE_ENV_DUMP", str(e.tmp / "env.json"))
    code, out = rnd(e, 1, "kimi")
    assert code == 0, out
    a = e.calls()[-1]
    assert a[a.index("-m") + 1] == "kimi-code/k3" and a[a.index("--agent-file") + 1].endswith("kimi-reviewer.md")
    empty = Path(a[a.index("--skills-dir") + 1])
    assert empty.is_dir() and not any(empty.iterdir()) and empty.parent == e.wt / "_review"
    assert a[-2:] == ["-p", "Read the file .parsec/brief.md and follow it exactly."]
    assert json.loads((e.tmp / "env.json").read_text(encoding="utf-8"))["KIMI_CODE_HOME"] == str(e.tmp / "kimi-home")
    assert e.record("design", 1, "kimi")["session"] == "session_2fc45d80-9dc5-4b9b-9561-65f39c787383"
    assert "- your lane, Kimi: read with your file tools only; you have no shell" in (e.wt / "_review" / "proj-09-22-x-design-kimi" / ".parsec" / "context.md").read_text(encoding="utf-8")   # lanes/kimi-reviewer.md disallows Bash
    code, out = rnd(e, 2, "kimi")
    a = e.calls()[-1]
    assert "--agent-file" not in a and a[a.index("--session") + 1] == "session_2fc45d80-9dc5-4b9b-9561-65f39c787383"


# row 2b: the Muse argument list, its session id and its child environment (2026-10-12 probes P1 to P4)
def test_muse_arguments_session_and_env(env):
    e = env
    e.mp.setenv("FAKE_STDOUT", "Summary.\n\nVERDICT: PASS\n")
    e.mp.setenv("FAKE_STDERR", "OpenAI Codex v9.9.9\n")   # pre-review F1: a codex-shaped line must not become a muse round's version
    e.mp.setenv("FAKE_ENV_DUMP", str(e.tmp / "env.json"))
    e.mp.setenv("META_API_KEY", "stray-key")
    code, out = rnd(e, 1, "muse")
    assert code == 0, out
    pairs = list(zip(a := e.calls()[-1], a[1:]))
    for flag in (("--contributor-mode", "off"), ("--sandbox-network", "restricted"), ("--model", "muse-wonder-full-1.0"), ("--effort", "high")):
        assert flag in pairs, (flag, a)
    assert a[0] == "exec" and all(f in a for f in ("--disable-write", "--disable-shell", "--disable-web-tools", "--disable-reminders", "--no-foreign-personal-context"))
    assert "--trust-workspace" not in a and a[-1] == "Read the file .parsec/brief.md and follow it exactly."
    sid = a[a.index("--session-id") + 1]
    rec = e.record("design", 1, "muse")
    assert str(uuid.UUID(sid)) == sid and rec["session"] == sid and rec["resumed"] is False and rec["verdict"] == "PASS" and rec["cli_version"] == "unknown"
    child = json.loads((e.tmp / "env.json").read_text(encoding="utf-8"))
    assert "META_API_KEY" not in child and child["MUSE_NO_AUTO_UPDATE"] == "1" and child["NO_COLOR"] == "1"
    assert "- your lane, Muse: read with your file tools only; you have no shell" in (e.wt / "_review" / "proj-09-22-x-design-muse" / ".parsec" / "context.md").read_text(encoding="utf-8")
    assert rnd(e, 2, "muse")[0] == 0
    a = e.calls()[-1]
    assert a[a.index("--session-id") + 1] == sid and e.record("design", 2, "muse")["resumed"] is True
    assert "CONTINUITY:" in (e.feat / "rounds" / "design-r2-muse" / "brief.md").read_text(encoding="utf-8")
    rnd(e, 3, "muse", "design", "--fresh")
    a = e.calls()[-1]
    assert a[a.index("--session-id") + 1] != sid and e.record("design", 3, "muse")["resumed"] is False
    folder = e.home / ".local" / "share" / "muse" / "sessions" / "2026" / "10" / "12" / sid
    folder.mkdir(parents=True)
    (folder / "session.jsonl").write_text("{}\n", encoding="utf-8")
    assert parsec.muse_session_file(sid) == folder / "session.jsonl" and parsec.muse_session_file(str(uuid.uuid4())) is None   # P4: the watcher's only growing file


# row 2c: the Neon argument list, its read rules, reply, session and child environment (2026-11-20 probes P2 to P8, C1, C4, C7; design round 1)
def test_neon_arguments_reply_and_session(env):
    e = env
    ok = json.dumps({"conversation_id": "aa62064a-0000-4000-8000-000000000001", "status": "SUCCESS", "response": "Summary.\n\nVERDICT: PASS\n"})
    for k, v in (("FAKE_STDOUT", ok), ("FAKE_ENV_DUMP", str(e.tmp / "env.json")), ("GEMINI_API_KEY", "stray-key"), ("FAKE_AGY_LOG", "I1120 03:42:30.932443 1 cli_setting_manager.go:98] CLI settings initialized: permissions=&{Allow:[] Deny:[write_file(*) command(*) read_url(*) execute_url(*) mcp(*)] Ask:[]}, toolPermission=request-review\n")): e.mp.setenv(k, v)   # 2026-11-20: a working key of unknown source and billing, never used; P8: the log line of the applied settings
    with open(e.repo / ".claude" / "parsec.toml", "a", encoding="utf-8") as f: f.write(f'[[context]]\npath = "{(e.tmp / "look").as_posix()}"\nrole = "lookup"\n[[context]]\npath = "{(e.tmp / "refs").as_posix()}"\nrole = "reference-code"\n')
    code, out = rnd(e, 1, "neon", "design", "--reference", "mod")
    a, tree, folder = (e.calls() or [[]])[-1], e.wt / "_review" / "proj-09-22-x-design-neon", e.feat / "rounds" / "design-r1-neon"   # no call yet on the base tool: the empty fallback lets the red run reach the exit-code assert below (Sol R2 F1, Astra F17)
    assert code == 0 and "### 🟢 Neon R1 Design Round: PASS" in out and (folder / "agy.json").is_file() and (folder / "agy.log").is_file(), out
    assert a[a.index("-p") + 1] == "Read the file .parsec/brief.md and follow it exactly." and a[a.index("--model") + 1] == "gemini-4-neon-high" and a[a.index("--output-format") + 1] == "json" and a[a.index("--add-dir") + 1] == str(tree.resolve()) and a[a.index("--log-file") + 1] == str((folder / "agy.log").resolve()) and "--mode" not in a and "--conversation" not in a   # P4: no mode, auto with the deny rules
    assert (perms := json.loads(a[a.index("--settings") + 1])["permissions"])["allow"] == [f"read_file({p.resolve().as_posix()})" for p in (e.repo / "AGENTS.md", e.tmp / "look", e.tmp / "refs" / "mod")] and sorted(perms["deny"]) == ["command(*)", "execute_url(*)", "mcp(*)", "read_url(*)", "write_file(*)"], perms   # C7: a path context.md names outside the tree was soft-denied without its rule
    assert "GEMINI_API_KEY" not in (child := json.loads((e.tmp / "env.json").read_text(encoding="utf-8"))) and child["AGY_CLI_DISABLE_AUTO_UPDATE"] == "true" and child["NO_COLOR"] == "1"
    assert (folder / "reply.md").read_text(encoding="utf-8") == "Summary.\n\nVERDICT: PASS\n" and (rec := e.record("design", 1, "neon"))["session"] == "aa62064a-0000-4000-8000-000000000001" and rec["verdict"] == "PASS" and rec["resumed"] is False and "- your lane, Neon: read with your file tools only; you have no shell" in (tree / ".parsec" / "context.md").read_text(encoding="utf-8")
    assert rnd(e, 2, "neon")[0] == 0 and (a := e.calls()[-1])[a.index("--conversation") + 1] == "aa62064a-0000-4000-8000-000000000001" and e.record("design", 2, "neon")["resumed"] is True and "CONTINUITY:" in (e.feat / "rounds" / "design-r2-neon" / "brief.md").read_text(encoding="utf-8") and len(json.loads(a[a.index("--settings") + 1])["permissions"]["allow"]) == 2   # no --reference, no reference rule (Sol R2 F5)
    assert rnd(e, 3, "neon", "design", "--fresh")[0] == 0 and "--conversation" not in e.calls()[-1]
    assert (r := rnd(e, 4, "neon", "design", "--fresh", "--reference", "../out"))[0] == 64 and "resolves outside the reference-code folder" in r[1] and run(e, "round", "prepare", "--feature", "09-22-x", "--kind", "design", "--round", "1", "--lane", "opus", "--brief", str(e.brief), "--head", e.head, "--reference", "../out")[0] == 64 and not (e.feat / "rounds" / "design-r1-opus").exists() and not (e.feat / "rounds" / "design-r4-neon").exists()   # Brandon, Q5-A (2026-11-20): every lane refuses a reference outside its folder; a Neon folder rule opens all below it (Sol F4, Astra F4; Sol R2 F5)
    e.mp.setenv("FAKE_STDOUT", json.dumps({"conversation_id": "c4", "status": "ERROR", "error": "print timeout after 30s", "finished_reason": "print_timeout"})); code, out = rnd(e, 4, "neon", "design", "--fresh")   # C4: a cut run has no response
    assert code == 65 and (r := e.record("design", 4, "neon"))["verdict"] == "NONE" and all(w in r["warnings"] and f"warning: {w}" in out for w in ("agy status ERROR: print timeout after 30s", "agy finished_reason: print_timeout")), out
    e.mp.setenv("FAKE_STDOUT", json.dumps({"conversation_id": "c5", "status": "SUCCESS", "response": "Reading it.\n\nVERDICT: PASS\n", "denied_actions": [{"action": "read_file"}]})); code, out = rnd(e, 4, "neon", "design", "--fresh"); assert code == 65 and e.record("design", 4, "neon")["verdict"] == "NONE" and "warning: a soft-denied step ended the run" in out and not (e.feat / "rounds" / "design-r4-neon" / "reply.md").exists(), out   # P3, C7: a soft-denied step ends the run; its partial text never counts (Sol F6)
    e.mp.setenv("FAKE_STDOUT", "not json"); code, out = rnd(e, 4, "neon", "design", "--fresh"); assert code == 65 and "warning: agy status NONE: agy.json is missing or not one JSON object" in out and not (e.feat / "rounds" / "design-r4-neon" / "reply.md").exists() and e.record("design", 4, "neon")["session"] == "unknown", out   # no id in agy.json nor the pending record (Astra F36)
    (f4 := e.feat / "rounds" / "design-r4-neon").joinpath("pending.json").write_text(json.dumps(dict(e.record("design", 4, "neon"), session="pending-id")), encoding="utf-8"); (f4 / "record.json").unlink(); (f4 / "reply.md").write_text("VERDICT: PASS\n", encoding="utf-8"); (f4 / "agy.json").write_text(json.dumps({"status": "SUCCESS", "response": "VERDICT: PASS\n"}), encoding="utf-8")   # a stale reply, and a clean object with no conversation id from a run the cap ended (Sol R2 F4, Astra F10, F36)
    assert parsec.collect(str(e.repo), "09-22-x", "design", 4, "neon", run={"cli_exit": None, "seconds": 1, "timeout": True}) == 67 and not (f4 / "reply.md").exists() and (r := e.record("design", 4, "neon"))["verdict"] == "NONE" and r["session"] == "pending-id"   # the run result round run passes on the cap; the session falls back to the pending one
    e.mp.setenv("FAKE_AGY_LOG", "CLI settings initialized: permissions=&{Allow:[] Deny:[write_file(*) command(*)] Ask:[]}\n"); e.mp.setenv("FAKE_STDOUT", ok); assert (r := rnd(e, 4, "neon", "design", "--fresh"))[0] == 65 and "warning: agy.log shows no deny rules, or not all of AGY_DENY" in r[1] and e.record("design", 4, "neon")["verdict"] == "NONE" and not (f4 / "reply.md").exists(), r[1]; e.mp.setenv("FAKE_STDOUT", json.dumps({"status": "SUCCESS", "response": " "})); assert (r := rnd(e, 4, "neon", "design", "--fresh"))[0] == 65 and all(f"warning: {w}" in r[1] for w in ("agy response is blank or missing", "agy.log shows no deny rules, or not all of AGY_DENY")), r[1]   # Sol diff r1 F3: the short log alone holds back a clean run's PASS; Fable F2, F4: a blank response, and a log that lacks three deny rules
    agent_dirs = (".Agents", ".Agent", "_AGENTS", "_Agent"); [((e.repo / a).mkdir(), (e.repo / a / "hooks.json").write_text("{}\n", encoding="utf-8")) for a in agent_dirs]; git("add", *(f"{a}/hooks.json" for a in agent_dirs), cwd=e.repo); git("commit", "-qm", "hooks", cwd=e.repo); e.head, n = git("rev-parse", "HEAD", cwd=e.repo), len(e.calls())   # 2026-11-20 build-time finding: agy ran the reviewed tree's .agents/hooks.json; the folders' case differs, which Windows ignores (security review); Fable last look r1 F1: the four names of agy's skill agy-customizations, each of which ran a hooks.json
    assert (r := rnd(e, 4, "neon", "design", "--fresh"))[0] == 64 and "tracks .Agent, .Agents, _AGENTS, _Agent," in r[1] and len(e.calls()) == n and e.record("design", 4, "neon")["verdict"] == "NONE", r[1]   # refused before anything is written: no launch, the round-4 record as it was (Brandon: "Refuse such a tree (Recommended)"; Q7: "Refuse all four (Recommended)"); every root entry named, in tree order
    assert run(e, "round", "close", "--feature", "09-22-x")[0] == 0 and not tree.exists()
    (d := e.tmp / "agy-direct").mkdir(); (d / "agy.log").write_text(f"CLI settings initialized: permissions=&{{Allow:[] Deny:[{' '.join(parsec.AGY_DENY)}] Ask:[]}}\n", encoding="utf-8"); (d / "agy.json").write_bytes(b'{"status": "SUCCESS", "response": "\xff\\nVERDICT: PASS\\n"}'); assert (w := parsec.agy_reply(d)[1]) == ["agy status NONE: agy.json is missing or not one JSON object"] and not (d / "reply.md").exists(), w   # Sol diff r1 F1: a byte that is not UTF-8 inside the response; replaced, it parsed to a clean object and a PASS
    (d / "agy.json").write_text(json.dumps({"status": "SUCCESS", "response": "VERDICT: PASS\n"}), encoding="utf-8"); (d / "reply.md").write_text("VERDICT: PASS\n", encoding="utf-8"); e.mp.setattr(parsec, "read_text", lambda p: (_ for _ in ()).throw(PermissionError(13, "held open", str(p)))); assert (w := parsec.agy_reply(d)[1]) == ["agy.log shows no deny rules, or not all of AGY_DENY: the read-only settings may not have applied"] and not (d / "reply.md").exists(), w   # Sol diff r1 F2: a log present but not readable is no evidence of the deny rules; it raised and left the round pending (last: the patch holds to the test's end)


# row 4: the brief reaches standard input byte for byte (2026-09-17; 2026-08-11), the kind's insert added by the tool (2026-09-25 audit: seat briefs derived by shell edit)
def test_brief_bytes_reach_stdin(env):
    e = env
    e.mp.setenv("FAKE_STDIN_COPY", str(e.tmp / "stdin.bin"))
    rnd(e, 1)
    assert (e.tmp / "stdin.bin").read_bytes() == TRICKY.encode("utf-8")   # no part 3, a verdict-only rerun: no insert (pre-review F1)
    assert "no `## 3.` part outside a fence, so no insert" in "".join(e.record("design", 1, "astra")["warnings"])
    e.brief.write_bytes(b"# Brief\n\n## 2. Task\n\nread it\n\n## 3. Rules\n\n- r\n\n## 7. Final check\n")
    rnd(e, 2)
    sent = (e.feat / "rounds" / "design-r2-astra" / "brief.md").read_bytes()
    assert sent == b"# Brief\n\n## 2. Task\n\nread it\n\n### " + (REPO / "templates" / "brief-design.md").read_bytes().replace(b"\r\n", b"\n")[2:].rstrip(b"\n") + b"\n\n## 3. Rules\n\n- r\n\n## 7. Final check\n" + parsec.CONTINUITY.encode()   # resumed: the tool adds the line (2026-09-28 audit, gk-4)
    assert b"\n\nThe subject is `.parsec/spec.md`; `.parsec/context.md` names the rubric and each evidence file. The feature has no task list: after the go, the session writes the code and its tests from this spec, test first. Review the spec: behaviour left open, contradictions, cases it does not decide, a file, name, signature or call site in its Design section that does not exist or cannot work where it lands in the tree, and anything that would make correct code impossible. Check that every Behaviour case traces to the Goal and to a test or named check in its Testing section. A missing implementation is not a finding.\n\n## 3. Rules" in sent   # direct-build B2
    assert (e.tmp / "stdin.bin").read_bytes() == sent and e.record("design", 2, "astra")["brief_sha256"] == parsec.sha256(e.feat / "rounds" / "design-r2-astra" / "brief.md")
    prep = lambda kind, lane, *x: run(e, "round", "prepare", "--feature", "09-22-x", "--kind", kind, "--round", "2" if x else "1", "--lane", lane, "--brief", str(e.brief),
                                      "--head", e.head, *(["--base", e.base] if kind != "design" else []), *x)
    for kind, lane, want in (("design", "fable", [b"Design", b"Fable-look"]), ("lastlook", "fable", [b"Diff", b"Fable-look"]), ("prereview", "opus", [b"Diff"])):
        assert prep(kind, lane)[0] == 0
        pkg = (e.feat / "rounds" / f"{kind}-r1-{lane}" / ".parsec" / "brief.md").read_bytes()
        assert pkg.startswith(b"# Brief\n\n## 2. Task\n\nread it\n\n### ") and pkg.endswith(b"\n\n## 3. Rules\n\n- r\n\n## 7. Final check\n") and pkg.count(b" insert\n") == len(want)
        assert all(b"### " + w + b" insert" in pkg for w in want)
    (e.feat / "rounds" / "design-r1-fable" / "reply.md").write_text("VERDICT: FIX\n", encoding="utf-8")
    run(e, "round", "collect", "--feature", "09-22-x", "--kind", "design", "--round", "1", "--lane", "fable", "--agent-id", "a-1")
    clean = e.brief.read_bytes()
    e.brief.write_bytes(clean + b"\n### Fable-look insert\n\nx\n")
    code, out = prep("design", "fable", "--resume", "a-1")                 # Sol diff r1 F1: a confirming question carrying an insert
    assert code == 64 and "already carries an insert" in out and not (e.feat / "rounds" / "design-r2-fable").exists()
    e.brief.write_bytes(clean)
    assert prep("design", "fable", "--resume", "a-1")[0] == 0 and b" insert" not in (e.feat / "rounds" / "design-r2-fable" / "brief.md").read_bytes()   # the confirming question stays narrow
    e.brief.write_bytes(b"## 2. Task\n\n# Diff insert\n\n## 3. Rules\n")
    code, out = prep("diff", "opus")
    assert code == 64 and "already carries an insert" in out and not (e.feat / "rounds" / "diff-r1-opus").exists()
    e.brief.write_bytes(b"## 2. Task\n\n## 3. Rules\n\n## 6. Boundaries\n\n```\n## 7. Final check\n```\n")   # field audit 4: Moving Day phase 13's four design briefs ended at part 6 (3 NONE)
    assert prep("diff", "opus")[0] == rnd(e, 3)[0] == 64 and "no `## <n>. Final check` part" in prep("diff", "opus")[1] and not (e.feat / "rounds" / "diff-r1-opus").exists()
    e.brief.write_bytes(clean)   # field audit 4 (H9): summaries of 545 to 636 words went to Brandon, and md-11's appended amendments rode in every package
    put = lambda body: (e.feat / "spec.md").write_bytes(b"# Spec\n\n" + body) and prep("diff", "opus")   # write_bytes returns the byte count, never 0 here
    got = [put(b) for b in (b"## decision summary\n\n" + b"w " * 151 + b"\n", b"## Amendment 1 (design round 1), 2026-10-12\r\nx\r\n", b"## 8. Amendment (base c9b4b874)\n", b"## Change log\n", b"## Changelog\n", b"## Change record\n", b"## Questions from design round 1\n", b"## Decision summary\n\n" + b"w " * 75 + b"\n##not-a-heading\n" + b"w " * 75 + b"\n", b" ## Decision summary\n\n" + b"w " * 151 + b"\n", b"   ## Amendment 1\n")]   # a lower-case summary heading; md-11 with CRLF ends; md-13's numbered shape; each other change-log word (pre-review F5); a hash line that is text, and indented headings (Sol diff r1 F1, F2)
    assert [(c, w in o) for (c, o), w in zip(got, ("has 151 words, at most 150", "## Amendment 1 (design round 1), 2026-10-12 is an appended change log", "## 8. Amendment (base c9b4b874) is", "## Change log is", "## Changelog is", "## Change record is", "## Questions from design round 1 is", "has 151 words, at most 150", "has 151 words, at most 150", "## Amendment 1 is an appended change log"))] == [(64, True)] * 10 and not (e.feat / "rounds" / "diff-r1-opus").exists() and rnd(e, 3)[0] == 64 and prep("panel", "fable")[0] == 0   # round run shares the check; a panel packs no spec, so it passes beside a refused one (pre-review F5)
    assert put(b"## Decision summary\n\n" + b"w " * 150 + b"\n## 1. Goal\n\n" + b"w " * 200 + b"\n```\n## Amendment 1\n## v0.1.32 (2026-10-16)\n```\n### Change log\n## 4. `record.json` and its amendment lines\n## Functionality changes\n")[0] == put(b"## Decision summary\n\n" + b"w " * 150 + b"\n   ## 1. Goal\n\n" + b"w " * 200 + b"\n")[0] == 0   # a fence, a deeper level, a later word and a project section never fire; an indented heading ends the summary (Sol diff r1 F2)


# row 5: resume by the recorded id, never --last; the rerun rule (2026-09-01; the scoping note's seven briefs)
def test_rerun_rule(env):
    e = env
    e.mp.setenv("FAKE_REPLY", "cut off before the verd")
    code, out = rnd(e, 1)
    assert code == 65 and e.record("design", 1, "astra")["verdict"] == "NONE"
    assert rnd(e, 1, "astra", "design", "--file", str(e.feat / "rounds" / "design-r1-astra" / "reply.md"))[0] == 64   # 2026-09-23 Sol: the rename moved that evidence away mid-round
    e.mp.setenv("FAKE_REPLY", "ok\n\nVERDICT: PASS\n")
    code, out = rnd(e, 1)
    assert code == 0 and (e.feat / "rounds" / "design-r1-astra.dead1").is_dir()
    a = e.calls()[-1]
    assert a[a.index("resume") + 1] == "01a0c9a2-0000-4000-8000-000000000001" and "--last" not in a
    code, out = rnd(e, 1)
    assert code == 64 and "astra's next design round is 2" in out and rnd(e, 3, "kimi")[0] == 64   # 2026-09-22 KitnEssentials: a first round ran as r3
    e.mp.setenv("FAKE_STDOUT", "no header at all\n")
    code, out = rnd(e, 2, "astra", "design", "--fresh")
    assert e.record("design", 2, "astra")["session"] == "unknown"
    code, out = rnd(e, 3)
    assert "resume" not in e.calls()[-1] and "fresh round" in "".join(e.record("design", 3, "astra")["warnings"])
    old = e.feat / "rounds" / "design-r3-sol"                     # r1 (Sol): an old-style round with no verdict reruns under its number
    old.mkdir()
    (old / "record.json").write_text(json.dumps({"kind": "design", "round": 3, "lane": "sol", "verdict": "NONE", "end": "9"}), encoding="utf-8")
    assert rnd(e, 3, "sol", "design", "--fresh")[0] == 0 and (old.parent / "design-r3-sol.dead1" / "record.json").is_file()
    stale = e.feat / "rounds" / "design-r4-kimi"                   # Kimi r2: an uncollected old-style round was refused toward round 1
    stale.mkdir()
    (stale / "pending.json").write_text("{}", encoding="utf-8")
    code, out = rnd(e, 4, "kimi")
    assert code == 64 and "never collected" in out


# row 5b: a symbolic --head resolves in the primary, not in a reused review worktree (2026-09-23, Astra)
def test_symbolic_head_resolved_in_primary(env):
    e = env
    args = ["round", "run", "--feature", "09-22-x", "--kind", "design", "--lane", "sol", "--brief", str(e.brief), "--head", "HEAD"]
    assert run(e, *args, "--round", "1")[0] == 0
    (e.repo / "code.txt").write_text("one\ntwo\nthree\n", encoding="utf-8")
    git("commit", "-qam", "later", cwd=e.repo)
    assert run(e, *args, "--round", "2")[0] == 0
    tree = e.wt / "_review" / "proj-09-22-x-design-sol"
    assert git("rev-parse", "HEAD", cwd=tree) == git("rev-parse", "HEAD", cwd=e.repo) == e.record("design", 2, "sol")["head"]


# row 6: verdict reading (old items 34 and 67; the 2026-09-21 Kimi replies)
@pytest.mark.parametrize("text,want", [
    ("VERDICT: PASS\n", "PASS"), ("  - **VERDICT: FIX** - a sentence after\n", "FIX"), ("> VERDICT: ESCALATE\n", "ESCALATE"),
    ("VERDICT: BLIND\n", "BLIND"), ("end with VERDICT: PASS, FIX or ESCALATE\n", "NONE"), ("VERDICT: FAIL\n", "NONE"),
    ("VERDICT: PASS\nmore text and the reply was cut", "NONE"), ("no verdict line\n", "NONE"), ("VERDICT: PA", "NONE"),   # 2026-09-25 audit: fld-10's Sol draft followed its verdict
    ("VERDICT: FIX\n\n  \n", "FIX"),
    ("• VERDICT: PASS smoke\n", "PASS")])   # 2026-09-24: a kimi 2.1.1 reply block
def test_verdict_reading(text, want):
    assert parsec.verdict_of(text) == want


def test_continuity_and_wrote_files(env):
    e = env
    rnd(e, 1)
    e.mp.setenv("FAKE_REPLY", "• CONTINUITY: FIX, the ledger point\n\nVERDICT: PASS\n")   # 2026-09-24: kimi starts each reply block with "• "
    rnd(e, 2)
    assert e.record("design", 2, "astra")["continuity"] == "FIX, the ledger point" and "continuity answered" in e.ledger().splitlines()[-1]
    e.mp.setenv("FAKE_REPLY", "VERDICT: PASS\n")
    e.brief.write_bytes(TRICKY.encode() + b"a quoted `CONTINUITY:` tag, and its line starting `CONTINUITY:`\n")   # pre-review F2, Sol diff r1 F3: a quote is not the question
    rnd(e, 3)
    assert e.record("design", 3, "astra")["continuity"] is None and "continuity: not answered" in e.ledger().splitlines()[-1]
    sent = lambda n: (e.feat / "rounds" / f"design-r{n}-astra" / "brief.md").read_bytes()
    assert sent(2).endswith(parsec.CONTINUITY.encode()) and b"CONTINUITY" not in sent(1) and sent(3).endswith(parsec.CONTINUITY.encode())   # 2026-09-28 audit: gk-4's derived briefs lost the line
    e.mp.setenv("FAKE_WRITE", str(e.wt / "_review" / f"proj-09-22-x-design-astra" / "ignored.txt"))
    code, out = rnd(e, 4)
    assert code == 66 and e.record("design", 4, "astra")["verdict"] == "WROTE-FILES"


# row 7: exit codes and the record a dead CLI leaves (2026-09-21 launch line; old item 32)
def test_exit_codes_and_dead_cli(env):
    e = env
    e.mp.setenv("FAKE_EXIT", "1")
    e.mp.setenv("FAKE_REPLY", "")
    code, out = rnd(e, 1)
    assert code == 65 and "cli exit: 1" in out and "transcript tail" in out
    r = e.record("design", 1, "astra")
    assert r["verdict"] == "NONE" and r["cli_exit"] == 1 and r["brief_sha256"] == parsec.sha256(e.feat / "rounds" / "design-r1-astra" / "brief.md")
    assert "design r1 astra: NONE, no reply" in e.ledger() and r["reply"] is None   # 2026-09-25 fld-15: it named the reply its rerun wrote
    e.mp.setenv("FAKE_EXIT", "3")
    e.mp.setenv("FAKE_REPLY", "VERDICT: PASS\n")
    code, out = rnd(e, 1)
    assert code == 3                                              # a missing feature folder: row 14's prepare, which round run shares


# row 8: the cap stops a fake that sleeps, its child included; the still-running line (old item 71)
@pytest.mark.skipif(not WIN, reason="taskkill")
def test_cap_kills_the_tree(env):
    e = env
    e.mp.setattr(parsec, "CAP_SECONDS", 3)
    e.mp.setattr(parsec, "STILL_MINUTES", (1 / 60,))
    e.mp.setenv("FAKE_SLEEP", "600")
    e.mp.setenv("FAKE_CHILD_PID_FILE", str(e.tmp / "child.pid"))
    t0 = time.time()
    code, out = rnd(e, 1)
    assert code == 67 and time.time() - t0 < 30 and "still running: 0 min, last write" in out   # 1/60 min prints as 0
    r = e.record("design", 1, "astra")
    assert r["verdict"] == "NONE" and any("TIMEOUT" in w for w in r["warnings"])
    pid = (e.tmp / "child.pid").read_text()
    alive = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True).stdout
    assert pid not in alive


# row 9: a writing reviewer, then the reuse rule (2026-07-24; old item 98)
def test_tree_reuse_after_writes(env):
    e = env
    tree = e.wt / "_review" / "proj-09-22-x-design-astra"
    rnd(e, 1)
    assert tree.is_dir()
    e.mp.setenv("FAKE_WRITE", str(tree / "code.txt"))          # a tracked edit
    code, out = rnd(e, 2)
    assert code == 66
    e.mp.delenv("FAKE_WRITE")
    ino = tree.stat().st_ctime_ns
    rnd(e, 2)
    assert tree.is_dir() and (tree / "code.txt").read_text() == "one\ntwo\n" and tree.stat().st_ctime_ns == ino
    e.mp.setenv("FAKE_WRITE", str(tree / "left.txt"))          # an untracked leftover
    code, out = rnd(e, 3)
    assert code == 66
    e.mp.delenv("FAKE_WRITE")
    rnd(e, 3)
    assert tree.is_dir() and not (tree / "left.txt").exists() and tree.stat().st_ctime_ns != ino
    other = e.wt / "_review" / "proj-09-22-x-more-design-astra"
    other.mkdir()
    code, out = run(e, "round", "close", "--feature", "09-22-x")
    assert code == 0 and not tree.exists() and other.is_dir()   # 2026-09-22 review: an unanchored prefix closed the neighbour


# row 10: remove-worktree, ten cases (2026-09-13; old item 107)
@pytest.mark.skipif(not WIN, reason="junctions")
def test_remove_worktree_cases(env):
    e = env
    review = e.wt / "_review"
    review.mkdir()

    def tree(name):
        p = review / name
        git("worktree", "add", "--detach", str(p), e.head, cwd=e.repo)
        return p

    def junction(link, target):
        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True, check=True)
    t = tree("a")
    (t / "ro.txt").write_text("x")
    os.chmod(t / "ro.txt", stat.S_IREAD)
    (t / "rodir").mkdir()
    (t / "rodir" / "f.txt").write_text("x")
    os.chmod(t / "rodir", stat.S_IREAD)
    target = e.tmp / "target"
    target.mkdir()
    (target / "keep.txt").write_text("keep")
    junction(t / "jn", target)
    junction(t / "dangling", e.tmp / "gone")
    assert run(e, "remove-worktree", str(t))[0] == 0 and not t.exists() and (target / "keep.txt").exists()
    t = tree("b")
    os.chmod(t, stat.S_IREAD)
    assert run(e, "remove-worktree", str(t))[0] == 0 and not t.exists()
    t = tree("c")
    with open(t / "held.txt", "w") as held:
        code, out = run(e, "remove-worktree", str(t))
        assert code != 0 and "held" in out and t.is_dir()
    assert run(e, "remove-worktree", str(t))[0] == 0 and not t.exists()
    assert run(e, "remove-worktree", str(review / "missing"))[0] == 64
    (review / "plain.txt").write_text("x")
    assert run(e, "remove-worktree", str(review / "plain.txt"))[0] == 64
    t = tree("d")
    junction(review / "link-root", t)
    code, out = run(e, "remove-worktree", str(review / "link-root"))
    assert code == 64 and "link" in out and (t / "code.txt").exists()
    (review / "stray").mkdir()
    assert run(e, "remove-worktree", str(review / "stray"))[0] == 64
    assert run(e, "remove-worktree", str(e.repo))[0] == 64 and (e.repo / "code.txt").exists()


# row 11: verify (Screenshot 1; Brandon 2026-09-21; old item 49)
def test_verify_states(env):
    e = env
    v = lambda *a: run(e, "verify", "--feature", "09-22-x", *a)
    assert v()[1].strip() == "NO-PASS-YET"
    assert v("--record-amendment", "too early")[0] == 64
    rnd(e, 1)                                                     # FIX
    assert v()[1].strip() == "NO-PASS-YET"
    e.mp.setenv("FAKE_REPLY", "VERDICT: PASS\n")
    rnd(e, 2)
    assert v()[1].strip() == "MATCH"
    run(e, "round", "collect", "--feature", "09-22-x", "--kind", "design", "--round", "2", "--lane", "astra", "--degraded", "kimi only")
    assert v()[1].strip() == "MATCH (DEGRADED PASS)"
    (e.feat / "spec.md").write_text("# Spec\n\nthe spec, amended\n", encoding="utf-8")
    assert v()[1].strip() == "CHANGED"
    run(e, "round", "prepare", "--feature", "09-22-x", "--kind", "panel", "--round", "1", "--lane", "fable", "--brief", str(e.brief))
    code, out = v("--record-amendment", "fix task for a gate finding")
    assert code == 64 and "panel-r1-fable is prepared but not collected" in out   # 2026-09-25 fld-14: an amendment landed before the FIX it answered
    (e.feat / "rounds" / "panel-r1-fable" / "reply.md").write_text("VERDICT: BLIND\n", encoding="utf-8")
    assert "no counts line" not in run(e, "round", "collect", "--feature", "09-22-x", "--kind", "panel", "--round", "1", "--lane", "fable")[1]   # field audit 4: 8 of 8 blind panel records warned
    code, out = v("--record-amendment", "fix task for a gate finding")
    assert code == 0 and f"amendment 1 recorded: spec {parsec.sha256(e.feat / 'spec.md')[:8]}\n" in out and v()[1].strip() == "MATCH (DEGRADED PASS)"   # the flag carries
    assert json.loads((e.feat / "rounds" / "amendment-1.json").read_text(encoding="utf-8"))["subject"] == {"spec": parsec.sha256(e.feat / "spec.md")}   # direct-build B4
    assert (e.feat / "rounds" / "amendment-1.json").is_file()
    assert rnd(e, 1, "sol", "diff")[0] == 0 and set(e.record("diff", 1, "sol")["subject"]) == {"spec"}   # Brandon, 2026-09-23 (A+): every gate seat checks the diff against the approved design
    assert "- amendment 1: fix task for a gate finding" in (e.wt / "_review" / "proj-09-22-x-diff-sol" / ".parsec" / "context.md").read_text(encoding="utf-8")
    e.mp.setenv("FAKE_REPLY", "VERDICT: FIX\n")
    rnd(e, 3)
    assert v()[1].strip() == "NO-PASS-YET" and v("--record-amendment", "after an unclosed FIX")[0] == 64
    run(e, "round", "collect", "--feature", "09-22-x", "--kind", "design", "--round", "3", "--lane", "astra", "--close-minor", "wording")
    assert v()[1].strip() == "MATCH (CLOSED ON MINOR)"
    (e.feat / "spec.md").write_text("changed\n", encoding="utf-8")
    assert v()[1].strip() == "CHANGED"


# direct-build B4 (2026-11-25): verify compares the spec alone; a 0.1.54 record of spec and tasks still reads; a missing spec never matches
def test_verify_spec_alone(env):
    e = env
    v = lambda *a: run(e, "verify", "--feature", "09-22-x", *a)
    (e.feat / "rounds" / "design-r1-fable").mkdir(parents=True)
    parsec.write_json(e.feat / "rounds" / "design-r1-fable" / "record.json", {"kind": "design", "verdict": "PASS", "end": "2026-11-20T10:00:00", "subject": {"spec": parsec.sha256(e.feat / "spec.md"), "tasks": "0" * 64}})
    assert v()[1].strip() == "MATCH"                                # no tasks.md
    (e.feat / "tasks.md").write_text("old list\n", encoding="utf-8")
    assert v()[1].strip() == "MATCH"                                # whatever it holds
    (e.feat / "spec.md").unlink()
    assert v()[1].strip() == "CHANGED"
    code, out = v("--record-amendment", "no spec")
    assert code == 64 and f"amendment refused: no spec.md in {e.feat}" in out and not list((e.feat / "rounds").glob("amendment-*")) and "amendment" not in e.ledger(), out
    parsec.write_json(e.feat / "rounds" / "amendment-1.json", {"time": "2026-11-21T10:00:00", "reason": "0.1.54 wrote it, then raised", "subject": {"spec": None, "tasks": None}, "degraded": None})
    (e.feat / "tasks.md").unlink()
    assert v()[1].strip() == "CHANGED"                              # a null spec never matches a missing file


# R7 (Astra diff r1 F4 of 0.1.55): records sort by instant, so in the hour repeated when the clocks go back verify reads the newer record; a stamp with no offset still reads
def test_records_sort_by_instant(env):
    e = env
    for name, end, verdict in (("design-r1-fable", "2026-11-01T01:30:00.000000-05:00", "PASS"), ("design-r2-fable", "2026-11-01T01:10:00.000000-06:00", "FIX"), ("design-r1-astra", "2026-10-31T10:00:00", "PASS"), ("design-r1-opus", "1969-12-31T10:00:00", "PASS")):   # Opus pre-review F1: Windows cannot convert a time before 1970
        (e.feat / "rounds" / name).mkdir(parents=True)
        parsec.write_json(e.feat / "rounds" / name / "record.json", {"kind": "design", "verdict": verdict, "end": end, "subject": {"spec": parsec.sha256(e.feat / "spec.md")}})
    assert run(e, "verify", "--feature", "09-22-x")[1].strip() == "NO-PASS-YET"   # 01:10 CST is 40 minutes after 01:30 CDT


# R6 (Astra diff r1 F1 of 0.1.55): the hash and the round's archived spec.md are the packaged bytes, even when the spec is saved again just after the copy
def test_packaged_spec_is_hashed(env):
    e = env
    sent, copy = (e.feat / "spec.md").read_bytes(), shutil.copyfile
    def save_after(src, dst):
        copy(src, dst)
        if Path(src) == e.feat / "spec.md" and Path(dst).parent.name == ".parsec": (e.feat / "spec.md").write_bytes(b"# Spec\n\nsaved later\n")
    e.mp.setattr(parsec.shutil, "copyfile", save_after)
    assert rnd(e, 1)[0] == 0
    assert e.record("design", 1, "astra")["subject"]["spec"] == parsec.hashlib.sha256(sent).hexdigest() and (e.feat / "rounds" / "design-r1-astra" / "spec.md").read_bytes() == sent


# R11 (Astra diff r3 F19 of 0.1.55): a --file reached through a junction in the round being rerun is read by the path prepare checked, not by its first spelling after the rename
def test_file_through_junction_in_rerun_round(env):
    e = env
    prep = lambda *a, f="09-22-x": run(e, "round", "prepare", "--feature", f, "--kind", "prereview", "--round", "1", "--lane", "opus", "--brief", str(e.brief), "--head", e.head, "--base", e.base, *a)
    folder, logs = e.feat / "rounds" / "prereview-r1-opus", e.tmp / "logs"
    assert prep()[0] == 0
    logs.mkdir(); (logs / "gate.log").write_text("green\n", encoding="utf-8")
    subprocess.run(["cmd", "/c", "mklink", "/J", str(folder / "j"), str(logs)], check=True, capture_output=True)
    code, out = prep("--file", str(folder / "j" / "gate.log"))
    assert code == 0 and (folder / ".parsec" / "evidence" / "1-gate.log").read_text(encoding="utf-8") == "green\n", out
    subprocess.run(["cmd", "/c", "mklink", "/J", str(alias := e.feat.with_name("09-22-alias")), str(e.feat)], check=True, capture_output=True)   # Sol diff r1 F2: a file inside the round, named through a feature junction, is refused before anything moves
    assert (r := prep("--file", str(alias / "rounds" / "prereview-r1-opus" / ".parsec" / "evidence" / "1-gate.log"), f="09-22-alias"))[0] == 64 and "inside prereview-r1-opus" in r[1] and (folder / "pending.json").is_file(), r[1]


# direct-build B2 (2026-11-25): a design round runs on spec.md alone and refuses without it, writing nothing
def test_design_round_on_spec_alone(env):
    e = env
    (e.feat / "spec.md").rename(e.tmp / "spec.md")
    for args in (["run", "--lane", "astra"], ["prepare", "--lane", "fable"]):
        code, out = run(e, "round", args[0], "--feature", "09-22-x", "--kind", "design", "--round", "1", *args[1:], "--brief", str(e.brief), "--head", e.head)
        assert code == 64 and f"design round without spec.md in {e.feat}" in out and not (e.feat / "rounds").exists(), out
    (e.tmp / "spec.md").rename(e.feat / "spec.md")
    (e.feat / "tasks.md").write_text("old list\n", encoding="utf-8")   # an older folder's list: not copied, packed or hashed
    assert rnd(e, 1)[0] == 0 and set(e.record("design", 1, "astra")["subject"]) == {"spec"}
    assert (e.feat / "rounds" / "design-r1-astra" / "spec.md").is_file() and not (e.feat / "rounds" / "design-r1-astra" / "tasks.md").exists()
    assert not (e.wt / "_review" / "proj-09-22-x-design-astra" / ".parsec" / "tasks.md").exists()


# direct-build B5 (2026-11-25): an older folder's tasks.md reaches a reviewer only as evidence, named by the brief or passed with --file
def test_legacy_tasks_md_is_evidence(env):
    e = env
    (e.feat / "tasks.md").write_text("old list\n", encoding="utf-8")
    other, upper, dead = e.tmp / "x" / "tasks.md", e.tmp / "y" / "TASKS.md", e.feat / "build" / "task-01-report.md.dead24"
    for f, body in ((other, "other list\n"), (upper, "upper list\n"), (dead, "old report\n")):
        f.parent.mkdir(); f.write_text(body, encoding="utf-8")
    (named := e.tmp / "named.md").write_text("# Brief\n\nRead `tasks.md`.\n", encoding="utf-8")
    folder, warn = e.feat / "rounds" / "prereview-r1-opus", "packed tasks.md from the feature folder as evidence (the brief named it)"

    def prep(brief, *files):                                         # (exit code, printed text, evidence name to text, subject keys)
        code, out = run(e, "round", "prepare", "--feature", "09-22-x", "--kind", "prereview", "--round", "1", "--lane", "opus", "--brief", str(brief),
                        "--head", e.head, "--base", e.base, *[x for f in files for x in ("--file", str(f))])
        ev = {q.name: q.read_text(encoding="utf-8") for q in (folder / ".parsec" / "evidence").glob("*")}
        got = (code, out, ev, set(json.loads((folder / "pending.json").read_text(encoding="utf-8"))["subject"]), (folder / ".parsec" / "tasks.md").exists())
        shutil.rmtree(folder)
        return got
    code, out, ev, subject, packed = prep(named)
    assert code == 0 and ev == {"1-tasks.md": "old list\n"} and warn in out and subject == {"spec"} and not packed, out
    code, out, ev, subject, packed = prep(e.brief)
    assert code == 0 and ev == {} and warn not in out and subject == {"spec"} and not packed, out
    code, out, ev, _, _ = prep(named, other)
    assert code == 0 and ev == {"1-tasks.md": "other list\n"} and warn not in out, out
    code, out, ev, _, _ = prep(named, upper)
    assert code == 0 and ev == {"1-TASKS.md": "upper list\n", "2-tasks.md": "old list\n"} and warn in out, out
    code, out, ev, _, _ = prep(e.brief, dead)
    assert code == 0 and ev == {"1-task-01-report.md.dead24": "old report\n"}, out


# row 12b: a `#` line in a fenced code block is no heading (2026-10-02, KitnEssentials 10-02 task 1: a fenced .toc file cut a brief at "## Title:")
def test_fenced_hash_line_is_no_heading(env):
    e = env
    head, task2 = b"# Plan\n\n## Global constraints\n\n- keep it\n\n", b"## Task 2: second\n\n- [ ] other\n"
    task1 = (b"## Task 1: the toc\n\n- **Files**: `a.toc`\n\n```toc title\n## Title: Kit\n~~~\n## Interface: 120100\n``` x\n## Notes: kit\n```\n\n"
             b"  ~~~~markdown\n## Task 9: quoted\n~~~\n## Step 1\n  ~~~~~\n\n```a` b\n")   # another mark, a run with text after it and a shorter run close nothing; a backtick info string opens nothing
    (e.tmp / "fence.md").write_bytes(head + task1 + task2)
    assert parsec.heading_index(e.tmp / "fence.md") == ["Plan", "Global constraints", "Task 1: the toc", "Task 2: second"]   # unfenced's closing rules, which prepare and the rubric reader use
    (e.tmp / "rub.md").write_text("# Rules\n\n```md\n# Fake\n```\n\n## Git\n", encoding="utf-8")
    assert parsec.heading_index(e.tmp / "rub.md") == ["Rules", "Git"]
    e.brief.write_bytes(b"## 2. Task\n\n```\n## 3. quoted\n# Diff insert\n```\n\n## 3. Rules\n## 4. Final check\n")
    out = parsec.assemble(e.brief, "diff", "sol", None, [])
    assert out.startswith(b"## 2. Task\n\n```\n## 3. quoted\n# Diff insert\n```\n\n### ") and out.endswith(b"\n\n## 3. Rules\n## 4. Final check\n")


# row 13: the doctor reads a stale install (old item 65)
def test_doctor_stale_install(env):
    e = env
    plug = e.home / ".claude" / "plugins"
    plug.mkdir(parents=True)
    inst = lambda entry: plug.joinpath("installed_plugins.json").write_text(json.dumps({"plugins": {"parsec@parsec": entry}}), encoding="utf-8")
    inst([{"version": "0.1.0", "gitCommitSha": "0" * 40}])
    e.mp.setattr(parsec, "PLUGIN", e.repo)
    code, out = run(e, "doctor")
    assert code == 0 and "STALE" in out and "bump it, then claude plugin update" in out and "\n- 🟢 **Claude Code:** fake-cli 1.0\n" in out   # 2026-09-22 17:16: update said "already latest"
    inst([{"version": "0.1.0", "gitCommitSha": e.head}])
    assert "0.1.0 at " in run(e, "doctor")[1] and "STALE" not in run(e, "doctor")[1]
    plug.joinpath("known_marketplaces.json").write_text(json.dumps({"parsec": {"installLocation": str(e.repo)}}), encoding="utf-8")
    (e.tmp / "cache-copy").mkdir()                                  # 2026-09-23: the cached copy is no git checkout, so the head read blank: STALE
    e.mp.setattr(parsec, "PLUGIN", e.tmp / "cache-copy")
    assert "🟢 **plugin install:** 0.1.0 at " in run(e, "doctor")[1]
    plug.joinpath("known_marketplaces.json").write_text("[]", encoding="utf-8")
    assert "repo head unknown" in run(e, "doctor")[1]               # a malformed marketplace file falls back, never a traceback
    inst([])
    assert run(e, "doctor")[0] == 0                                 # 2026-09-23 pre-review: an empty entry crashed every command
    plug.joinpath("installed_plugins.json").write_text("[]", encoding="utf-8")
    assert "not installed" in run(e, "doctor")[1]                   # 2026-09-23, Astra: a malformed file crashed the doctor
    inst([{"gitCommitSha": None}])
    assert "STALE" in run(e, "doctor")[1]                           # and so did a null commit (Astra r2)
    inst([{"version": "0.1.0", "gitCommitSha": e.head, "installPath": None}])
    e.mp.setattr(parsec, "PLUGIN", e.repo)
    (e.repo / ".claude-plugin").mkdir()
    (e.repo / ".claude-plugin" / "plugin.json").write_text('{"version": "0.0.9"}', encoding="utf-8")
    assert "the new tool is ?\n" in run(e, "doctor")[1]              # pre-review F6: a null path hid the whole warning; Sol diff r1 F3: "?" alone
    inst([{"version": "0.1.0", "gitCommitSha": e.head, "installPath": str(e.tmp / "c010")}])
    out = run(e, "doctor")[1]                                       # 2026-09-23: three phases ran 0.1.6 after 0.1.7; 2026-09-25: a re-invoked skill kept 0.1.13
    assert out.endswith("\nstale: this tool is parsec 0.0.9, but 0.1.0 is installed: this session's skills and templates stay at 0.0.9 until a new session, "   # field audit 4: a first line that grep -v "^warning" hid
                        f"so start one; the new tool is {e.tmp / 'c010' / 'tools' / 'parsec.py'}\n") and "warning: this tool" not in out
    e.mp.setenv("FAKE_VERSION", "codex-cli 0.159.2")                 # 2026-10-17: codex-cli 0.159.2 read green with 0.163.0 out
    (new := e.tmp / "latest.json").write_text('{"version": "0.163.0"}', encoding="utf-8")
    (e.tmp / "bad.json").write_text('{"version": "error 404"}', encoding="utf-8")   # Sol design r1 F2: no version token, so latest unknown and never version 404
    cmd = json.dumps([sys.executable, str(FAKE)])
    upd = json.dumps([sys.executable, str(FAKE), "update"])
    (e.tmp / "lanes.toml").write_text(f'[astra]\nmodel = "a"\neffort = "high"\ncommand = {cmd}\nupdate = {upd}\nlatest = "{new.as_uri()}"\n'
                                      f'[sol]\nmodel = "s"\neffort = "high"\ncommand = {cmd}\nupdate = {upd}\nlatest = "{new.as_uri()}"\n'
                                      f'[neon]\nmodel = "g"\neffort = "high"\ncommand = {cmd}\nupdate = {upd[:-1]}, "agy"]\nlatest = "{(e.tmp / "none.json").as_uri()}"\n'
                                      f'[muse]\nmodel = "m"\neffort = "high"\ncommand = {cmd}\nupdate = {upd[:-1]}, "muse"]\nlatest = "{(e.tmp / "bad.json").as_uri()}"\n', encoding="utf-8")
    e.mp.setenv("FAKE_ENV_DUMP", str(e.tmp / "env.json"))
    code, out = run(e, "doctor", "--update")
    assert code == 0 and [c for c in e.calls() if c[:1] == ["update"]] == [["update"], ["update"], ["update", "agy"], ["update", "muse"]]   # 2026-09-22 review: codex updated twice; Claude Code first
    dump = json.loads((e.tmp / "env.json").read_text(encoding="utf-8"))
    assert dump["AGY_CLI_DISABLE_AUTO_UPDATE"] == "true" and dump["MUSE_SYNC_UPDATE"] == "1" and "- **update Claude Code:** exit 0" in out   # 2026-10-12: muse has no update subcommand; its launcher updates in the foreground
    e.mp.setattr(parsec, "CLAUDE", ["parsec-no-such-claude"])        # Brandon, 2026-10-16: "it should check and update the Claude code cli"
    assert "\n- 🔴 **Claude Code:** parsec-no-such-claude not found on PATH\n" in run(e, "doctor")[1]
    (e.home / ".config" / "muse").mkdir(parents=True); (e.home / ".config" / "muse" / "auth.json").write_text("{}", encoding="utf-8"); (e.wt / "t1").mkdir()
    e.mp.setattr(parsec, "CLAUDE_LATEST", new.as_uri())                # a red row makes no lookup, so its row gets no tail
    out = run(e, "doctor")[1]                                       # 2026-10-17: one row per CLI (Brandon); a CLI behind its latest release read green
    assert "\n- 🟢 codex-cli 0.159.2, Logged in using ChatGPT: astra (a, high), sol (s, high)\n  - 🟡 behind: 0.159.2 installed, 0.163.0 is out\n" in out and "\n- 🟢 codex-cli 0.159.2, login in the first run's log: neon (g, high) · latest unknown\n" in out and "\n- 🟢 codex-cli 0.159.2, auth.json present: muse (m, high) · latest unknown\n" in out and "\n- 🔴 **Claude Code:** parsec-no-such-claude not found on PATH\n- 🟢 **config:** ok\n\n**Lane CLIs**\n" in out and "\n\nnext: run /parsec:doctor update: a CLI above is behind its latest release\nstale: this tool is parsec 0.0.9" in out, out
    (same := e.tmp / "same.json").write_text('{"version": "0.159.2-R2"}', encoding="utf-8")   # current: only a build suffix differs, as a muse -R release
    e.mp.setattr(parsec, "CLAUDE", [sys.executable, str(FAKE)]); e.mp.setattr(parsec, "CLAUDE_LATEST", same.as_uri())
    out = run(e, "doctor")[1]
    assert out.startswith("### 🟡 parsec doctor\n\n**Claude Code**\n- 🟢 **plugin install:** ") and "\n- 🟢 **Claude Code:** codex-cli 0.159.2\n- 🟢 **config:** ok\n" in out and "\n\n**Worktrees**\n- **worktrees:** t1, 0 d old\n" in out, out
    (big := e.tmp / "big.json").write_text('{"version": "9.9.9", "pad": "' + "x" * (1 << 20) + '"}', encoding="utf-8"); e.mp.setattr(parsec, "CLAUDE_LATEST", big.as_uri())   # Sol diff r1 F3: an answer over 1 MiB is cut, so it is no version
    assert "\n- 🟢 **Claude Code:** codex-cli 0.159.2 · latest unknown\n" in run(e, "doctor")[1]
    (cut := e.tmp / "cut.txt").write_bytes(b"9.9.9" + b" " * ((1 << 20) - 5) + b"</html>"); e.mp.setattr(parsec, "CLAUDE_LATEST", cut.as_uri())   # Sol diff r2 F4: its first MiB strips to 9.9.9, but the whole answer is no version
    assert "\n- 🟢 **Claude Code:** codex-cli 0.159.2 · latest unknown\n" in run(e, "doctor")[1]
    assert "next: run" not in run(e, "doctor", "--update")[1]                # a guard, green on the base too (Sol design r1 F4)
    look = lambda ver, body, after="": (e.mp.setenv("FAKE_VERSION", ver), (e.tmp / "l.txt").write_text(body, encoding="utf-8"), (e.tmp / "lanes.toml").write_text(f'[neon]\nmodel = "g"\neffort = "high"\ncommand = {cmd}\nlatest = "{(e.tmp / "l.txt").as_uri()}"\nlatest_after = "{after}"\n', encoding="utf-8"), run(e, "doctor")[1].split("neon (g, high)", 1)[1])[3]   # the text after the one lane row
    assert [look("0.164.0-alpha.2", "0.164.0").startswith("\n  - 🟡 behind: 0.164.0-alpha.2 installed, 0.164.0 is out\n"), look("2.2", "2.2.0").startswith("\n\n**Worktrees**\n"), look("1.2.3+b", "1.2.4").startswith("\n  - 🟡 behind: 1.2.3+b installed, 1.2.4 is out\n")] == [True, True, True]   # item 2, Q2-A (Brandon, 2026-10-17): a pre-release read current, and 2.2 read behind 2.2.0; Sol design r1 F4 of 0.1.40: the installed version printed whole
    assert [look("1.2.16", "Antigravity CLI auto updater is running! Stable Version: 1.4.2. Rolled out to 100%", "Stable Version: ").startswith("\n  - 🟡 behind: 1.2.16 installed, 1.4.2 is out\n"), look("1.2.16", "9.9.9", "Stable Version: ").startswith(" · latest unknown\n")] == [True, True]   # item 1 (Brandon, 2026-10-17): agy's banner as probe C1 read it; a lane with latest_after never falls back to a bare version


@pytest.mark.parametrize("ans, pad", [('{"id": 2, "result": "rateLimits"}', 0), ('{"id": 2, "result": {"rateLimits": "x"}}', 0), ('{"id": 2, "result": {"rateLimits": {}}}', 1 << 20), ('{"id": 2, "result": {"rateLimits": {"primary": false}}}', 0), ('{"id": 2, "error": {"message": "rateLimits"}}', 0)])
def test_quota_bad_answer_reads_unavailable(env, ans, pad):   # probe C3, 2026-10-17: a result that is no object crashed the pre-flight; Q5-A (Brandon): an answer line over 1 MiB is no answer; Sol design r1 F2, F3 of 0.1.40: a window that is no object, and an answer without result
    (env.tmp / "q.json").write_text(ans + " " * pad, encoding="utf-8"); env.mp.setenv("FAKE_QUOTA", str(env.tmp / "q.json"))
    assert "**Quota:** unavailable" in run(env, "doctor", "--lane", "astra", "--kind", "design", "--feature", "09-22-x")[1]


# row 14: inputs, the pre-flight, the in-session package (old item 100; the 2026-09-21 dry run and Kimi login; "in this directory")
def test_inputs_and_preflight(env):
    e = env
    code, out = run(e, "round", "prepare", "--feature", "09-22-y", "--kind", "design", "--round", "1", "--lane", "opus",
                    "--brief", str(e.brief), "--head", e.head)
    assert code == 64 and not (e.repo / "docs" / "09-22-y").exists()
    code, out = run(e, "verify", "--feature", "../09-22-x")
    assert code == 64 and "not under the docs root" in out      # 2026-09-22 review: --feature could climb out of the docs root
    (e.repo / ".claude" / "parsec.toml").rename(e.repo / ".claude" / "off.toml")
    assert (r := run(e, "doctor", "--lane", "astra", "--kind", "design", "--feature", "09-22-x"))[0] == 64 and "run setup first" in r[1]
    assert (r := run(e, "doctor"))[0] == 64 and r[1].startswith("### 🔴 parsec doctor\n\n**Claude Code**\n") and "\n- 🔴 **config:** " in r[1]   # 2026-09-22 review: the table printed "config:" and exited 0
    (e.repo / ".claude" / "off.toml").rename(e.repo / ".claude" / "parsec.toml")
    (e.repo / "AGENTS.md").rename(e.repo / "A.md")
    assert (r := run(e, "doctor", "--lane", "astra", "--kind", "design", "--feature", "09-22-x"))[0] == 64 and "rubric file not found" in r[1]   # 2026-09-22 review: a missing rubric file only warned
    (e.repo / "A.md").rename(e.repo / "AGENTS.md")
    code, out = run(e, "doctor", "--lane", "astra", "--kind", "design", "--feature", "09-22-x")
    assert code == 0 and "2 of 2 sections found" in out and "fast off" in out and out.startswith("### 🟢 Pre-flight: Astra"), out
    assert out.endswith("rides in the next Astra summary\n") and (e.feat / "rounds" / "preflight-astra.txt").is_file()   # 2026-10-04 Afterparty: 2 of 5 posted
    assert "(lanes.toml), fast\n" in run(e, "doctor", "--lane", "astra", "--kind", "design", "--feature", "09-22-x", "--fast")[1]
    assert run(e, "doctor", "--lane", "opus", "--kind", "design", "--feature", "docs/09-22-x")[0] == 0   # 2026-09-23: the docs-root prefix was refused by round run only
    assert (r := run(e, "doctor", "--lane", "opus", "--kind", "panel", "--feature", "panels/09-23-new"))[0] == 0 and r[1].endswith("post the block above in chat now, as is, outside a code block\n")   # a new panel's pre-flight passes, for a panel round only (2026-09-23, Sol); no folder carries it (pre-review F1)
    assert run(e, "doctor", "--lane", "opus", "--kind", "design", "--feature", "panels/09-23-new")[0] == 64
    git("worktree", "add", "--detach", str(e.tmp / "side"), e.head, cwd=e.repo)   # 2026-10-17 KitnUI: a worktree session's seat could not write its reply into the primary's docs root
    e.mp.chdir(e.tmp / "side")                                    # the session's own folder, whatever --repo names (Sol diff r2 F1)
    assert run(e, "doctor", "--lane", "fable", "--kind", "design", "--feature", "09-22-x")[0] == 0   # a terminal session is not guarded (Sol diff r1 F1)
    e.mp.setenv("CLAUDE_CODE_ENTRYPOINT", "claude-desktop")
    assert run(e, "doctor", "--lane", "fable", "--kind", "design", "--feature", "09-22-x")[1].startswith("### 🔴 Pre-flight: Fable · design debate · FAILED\n\n**the docs root")
    e.mp.chdir(e.repo)
    assert run(e, "--repo", str(e.tmp / "side"), "doctor", "--lane", "fable", "--kind", "design", "--feature", "09-22-x")[0] == 0   # a desktop session in the primary passes
    assert (r := run(e, "doctor", "--lane", "opus", "--kind", "design", "--feature", "09-22-nope"))[0] == 64 and r[1].startswith("### 🔴 Pre-flight: Opus · design debate · FAILED")   # and doctor never checked --feature at all
    (e.repo / "AGENTS.md").write_text("# Rules\n\n## Lua style (renamed)\n\n## Git\n", encoding="utf-8")
    assert (r := run(e, "doctor", "--lane", "astra", "--kind", "design", "--feature", "09-22-x"))[0] == 64 and 'section not found: "Lua style"' in r[1] and not [p for p in (e.feat / "rounds").iterdir() if p.is_dir()]
    assert not (e.feat / "rounds" / "preflight-astra.txt").exists()   # pre-review F2: no older green line rides after a FAILED one
    (e.repo / "AGENTS.md").write_text("# Rules\n\n## Lua style\n\n## Git\n", encoding="utf-8")
    e.mp.setenv("FAKE_LOGIN", "Not logged in")
    assert run(e, "doctor", "--lane", "astra", "--kind", "design", "--feature", "09-22-x")[0] == 64
    e.mp.delenv("FAKE_LOGIN")
    conf = e.tmp / "kimi-home" / "config.toml"
    conf.write_text('default_effort = "high"\n', encoding="utf-8")
    code, out = run(e, "doctor", "--lane", "kimi", "--kind", "design", "--feature", "09-22-x")
    assert code == 64 and "not in the lane home" in out          # 2026-09-22 review: the Kimi line passed for another reason
    conf.write_text('[models."kimi-code/k3"]\ndefault_effort = "high"\n', encoding="utf-8")
    assert run(e, "doctor", "--lane", "kimi", "--kind", "design", "--feature", "09-22-x")[0] == 0
    code, out = run(e, "doctor", "--lane", "nope", "--kind", "design", "--feature", "09-22-x")
    assert code == 64 and "not a lane or a seat" in out          # 2026-09-22 review: a typo raised KeyError
    e.mp.setenv("FAKE_CHILD_PID_FILE", str(e.tmp / "quota.pid"))
    t0 = time.time()
    code, out = run(e, "doctor", "--lane", "astra", "--kind", "design", "--feature", "09-22-x")
    assert code == 0 and "**Quota:** 5 h 60% left" in out and time.time() - t0 < 8, out   # r4 (Sol): the reader returns at its first answer
    pid = (e.tmp / "quota.pid").read_text()
    assert not WIN or pid not in subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True).stdout   # r3 (Sol): the .CMD's child outlived the probe
    e.mp.delenv("FAKE_CHILD_PID_FILE")
    p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])   # 0.1.40 Sol diff r1 F1: a taskkill that could not start raised out of kill_tree and left the child alive
    with pytest.MonkeyPatch.context() as m: m.setattr(parsec.subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(OSError("no taskkill"))); parsec.kill_tree(p)
    assert p.poll() is not None
    for used, mark in (("85", "🟡"), ("96", "🔴")):                # G-Q2 (Brandon, 2026-10-16); field audit 4: "week 4% left" read green, then Sol died after 575 s
        e.mp.setenv("FAKE_USED", used)
        code, out = run(e, "doctor", "--lane", "astra", "--kind", "design", "--feature", "09-22-x")
        assert code == 0 and out.startswith(f"### {mark} Pre-flight: Astra · design debate · quota {100 - int(used)}% left") and out.endswith("outside a code block\n") and not (e.feat / "rounds" / "preflight-astra.txt").exists()
    e.mp.delenv("FAKE_USED")
    bad = e.tmp / "bad-lanes.toml"
    bad.write_text('[astra]\nmodel = "gpt-6-astra"\neffort = "high"\ncommand = ["no-such-program-xyz"]\n', encoding="utf-8")
    e.mp.setattr(parsec, "LANES_FILE", bad)
    assert run(e, "doctor", "--lane", "astra", "--kind", "design", "--feature", "09-22-x")[0] == 64
    assert rnd(e, 1)[0] == 64
    e.mp.setattr(parsec, "LANES_FILE", e.tmp / "lanes.toml")
    extra = e.tmp / "reply-r1.md"
    extra.write_text("earlier reply", encoding="utf-8")
    code, out = run(e, "round", "prepare", "--feature", "09-22-x", "--kind", "prereview", "--round", "1", "--lane", "opus",
                    "--brief", str(e.brief), "--head", e.head, "--base", e.base, "--file", str(extra), "--file", str(e.brief))
    folder = e.feat / "rounds" / "prereview-r1-opus"
    assert code == 0 and "Opus Pre-Review" in out and str(folder) in out and "diff.patch:" in out, out
    assert (folder / ".parsec" / "evidence" / "1-reply-r1.md").read_text() == "earlier reply"
    assert (folder / ".parsec" / "evidence" / "2-brief.md").is_file() and (folder / ".parsec" / "diff.patch").stat().st_size > 0
    page = int(out.split("Read pages ")[1].split()[0])              # 2026-09-24 fld-11: 2,000 lines of a 96 KB patch passed the Read cap
    assert page * (folder / ".parsec" / "diff.patch").stat().st_size <= 40000 * len((folder / ".parsec" / "diff.patch").read_text().splitlines()) or page == 100
    tree = e.wt / "_review" / "proj-09-22-x-prereview-opus"        # 2026-09-23: seven phases gave Opus and Fable the primary as the code root
    assert (folder / "pending.json").is_file() and git("rev-parse", "HEAD", cwd=tree) == e.head and f"code root: {tree}" in out
    ctx = (folder / ".parsec" / "context.md").read_text(encoding="utf-8")
    assert f"brief: {folder / '.parsec' / 'brief.md'}" in out and "evidence/1-reply-r1.md is a copy of reply-r1.md" in ctx and str(extra) not in ctx
    assert ctx.splitlines()[2].startswith("- your lane, Opus: read with your file tools only") and (folder / ".parsec" / "spec.md").is_file() and not (folder / ".parsec" / "tasks.md").exists()   # 2026-09-23 audit: Fable was told it had a shell
    assert "- design: .parsec/spec.md, the reviewed design\n- amendments: none" in ctx   # Brandon, 2026-09-23 (A+); reviewed, since a waived spec reading is no approval (batch F)
    bounded = e.repo / "docs" / "09-22-b"                           # bounded work has no design to pack
    bounded.mkdir()
    (bounded / "ledger.md").write_text("# Ledger\n", encoding="utf-8")
    assert run(e, "round", "prepare", "--feature", "09-22-b", "--kind", "diff", "--round", "1", "--lane", "fable", "--brief", str(e.brief), "--head", e.head, "--base", e.base)[0] == 0
    pkg = bounded / "rounds" / "diff-r1-fable" / ".parsec"
    assert "- design:" not in (pkg / "context.md").read_text(encoding="utf-8") and not (pkg / "spec.md").exists()
    (folder / "reply.md").write_text("report\n\nVERDICT: PASS\n", encoding="utf-8")
    (e.tmp / "session.jsonl").write_text(json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "content": out}]}}) + "\n", encoding="utf-8")   # Fable last look F1 of 0.1.55: the Stop hook reads the row this prepare printed
    stop = subprocess.run([sys.executable, str(REPO / "tools" / "hooks.py"), "stop"], input=json.dumps({"transcript_path": str(e.tmp / "session.jsonl"), "stop_hook_active": False}).encode(), capture_output=True).stdout
    assert "(pending.json is present) in 09-22-x\\rounds\\prereview-r1-opus. " in json.loads(stop)["reason"], stop
    code, out = run(e, "round", "collect", "--feature", "09-22-x", "--kind", "prereview", "--round", "1", "--lane", "opus")
    r = e.record("prereview", 1, "opus")
    assert code == 0 and r["verdict"] == "PASS" and r["agent"] == "reviewer-opus" and r["model"].startswith("claude-opus") and not (folder / "pending.json").exists()
    assert set(r["subject"]) == {"spec"}
    again = run(e, "round", "collect", "--feature", "09-22-x", "--kind", "prereview", "--round", "1", "--lane", "opus")[1]
    assert "in-session agent" in out and r["degraded"] is None and "already collected" in again and "round run" not in again   # 0.1.9 last look F2: an agent round has no round run
    run(e, "round", "prepare", "--feature", "09-22-x", "--kind", "lastlook", "--round", "1", "--lane", "opus", "--brief", str(e.brief), "--head", e.head, "--base", e.base)
    (e.feat / "rounds" / "lastlook-r1-opus" / "reply.md").write_text("VERDICT: PASS\n", encoding="utf-8")
    run(e, "round", "collect", "--feature", "09-22-x", "--kind", "lastlook", "--round", "1", "--lane", "opus")
    assert "stand-in" in e.record("lastlook", 1, "opus")["degraded"] and "lastlook r1 opus: PASS, degraded (stand-in" in e.ledger()   # 2026-09-23: six stand-ins read as a plain PASS
    code, out = run(e, "round", "prepare", "--feature", "docs/09-22-x", "--kind", "panel", "--round", "1", "--lane", "opus", "--brief", str(e.brief))
    assert code == 0 and (e.feat / "rounds" / "panel-r1-opus").is_dir() and (e.wt / "_review" / "proj-09-22-x-panel-opus").is_dir()   # 2026-09-23: the docs-root prefix was refused by round run
    code, out = run(e, "round", "prepare", "--feature", "09-22-x", "--kind", "panel", "--round", "1", "--lane", "fable",
                    "--brief", str(e.brief), "--head", e.head, "--file", str(extra), "--file", str(extra))
    assert code == 64 and "twice" in out
    code, out = run(e, "round", "prepare", "--feature", "09-22-x", "--kind", "panel", "--round", "1", "--lane", "fable",
                    "--brief", str(e.brief))                   # 2026-09-22 16:45: two panel rounds died wanting a range
    assert code == 0 and e.head.startswith(json.loads((e.feat / "rounds" / "panel-r1-fable" / "pending.json").read_text(encoding="utf-8"))["head"])
    fpkg = e.feat / "rounds" / "panel-r1-fable" / ".parsec"
    assert "- your lane, Fable: read with your file tools only" in (fpkg / "context.md").read_text(encoding="utf-8") and not (fpkg / "spec.md").exists()   # a panel packs no design
    code, out = run(e, "round", "prepare", "--feature", "09-22-x", "--kind", "panel", "--round", "1", "--lane", "fable", "--brief", str(e.brief))
    assert code == 0 and "the uncollected package is now panel-r1-fable.dead1" in out and (fpkg.parent.with_name("panel-r1-fable.dead1") / "pending.json").is_file()   # field audit 4: 4 slices hand-edited or deleted it
    code, out = run(e, "round", "prepare", "--feature", "09-22-x", "--kind", "design", "--round", "9", "--lane", "fable", "--brief", str(e.brief))
    assert code == 64 and "--head is required" in out
    assert run(e, "round", "prepare", "--feature", "09-22-x", "--kind", "design", "--round", "9", "--brief", str(e.brief), "--head", e.head)[0] == 2
    conf = e.repo / ".claude" / "parsec.toml"
    conf.write_text(conf.read_text(encoding="utf-8") + '[reviewer]\ncodex_lane = "astra"\n', encoding="utf-8")
    code, out = run(e, "round", "run", "--feature", "09-22-x", "--kind", "design", "--round", "1", "--brief", str(e.brief), "--head", e.head)
    assert code == 0 and e.record("design", 1, "astra")["lane"] == "astra"   # 2026-09-22 review: codex_lane was a key nothing read; r2 (Sol): run only, prepare needs its seat
    assert run(e, "round", "close", "--feature", "09-22-x", "--kind", "lastlook")[0] == 2   # r2 (Sol): a free string reached the name pattern; field audit 4: --kind lastlook left the diff worktree
    assert run(e, "round", "collect", "--feature", "09-22-x", "--kind", "panel", "--round", "1", "--lane", "fable")[0] == 65   # no reply yet: NONE
    rnd(e, 1, "kimi")
    seven = e.feat / "rounds" / "design-r1-kimi"                  # a killed run, its tree closed by hand, then a manual collect
    (seven / "pending.json").write_text(json.dumps({**e.record("design", 1, "kimi"), "worktree": str(e.tmp / "gone")}), encoding="utf-8")
    (seven / "record.json").unlink()
    (seven / "reply.md").write_text("VERDICT: PASS\n", encoding="utf-8")
    code, out = run(e, "round", "collect", "--feature", "09-22-x", "--kind", "design", "--round", "1", "--lane", "kimi")
    assert code == 65 and e.record("design", 1, "kimi")["verdict"] == "NONE" and "worktree missing" in out   # r2 (Sol): no PASS without the tree
    (seven / "pending.json").write_text(json.dumps({**e.record("design", 1, "kimi"), "worktree": None}), encoding="utf-8")
    keep = parsec.ledger_line
    e.mp.setattr(parsec, "ledger_line", lambda *a: 1 / 0)          # a stop between the record and the ledger line
    with pytest.raises(ZeroDivisionError):
        run(e, "round", "collect", "--feature", "09-22-x", "--kind", "design", "--round", "1", "--lane", "kimi")
    assert not (seven / "pending.json").exists() and e.record("design", 1, "kimi")["verdict"] == "PASS"   # r3 (Sol): no replay after the record
    e.mp.setattr(parsec, "ledger_line", keep)
    conf.write_text(conf.read_text(encoding="utf-8").replace('"astra"', '"neon"'), encoding="utf-8"); assert (q := run(e, "round", "run", "--feature", "panels/09-22-bad", "--kind", "panel", "--round", "1", "--brief", str(e.brief)))[0] == 64 and "runs only by name: pass --lane neon" in q[1] and not (e.repo / "docs" / "panels" / "09-22-bad").exists()   # Brandon, Q4-A (2026-11-20): Neon runs only with --lane neon, never as the config's default
    conf.write_text(conf.read_text(encoding="utf-8").replace('"neon"', '"opus"'), encoding="utf-8")
    code, out = run(e, "round", "run", "--feature", "panels/09-22-bad", "--kind", "panel", "--round", "1", "--brief", str(e.brief))
    assert code == 64 and "is not a lane" in out and not (e.repo / "docs" / "panels" / "09-22-bad").exists()   # r3, r4 (Sol): a config typo wrote a package, then a panel folder
    code, out = run(e, "round", "prepare", "--feature", "panels/09-22-t", "--kind", "panel", "--round", "3", "--lane", "fable", "--brief", str(e.brief))
    assert code == 64 and "a new panel's first round is 1" in out and not (e.repo / "docs" / "panels" / "09-22-t").exists()   # r1 (Sol): a wrong first number made the panel folder
    code, out = run(e, "round", "prepare", "--feature", "panels/09-22-t", "--kind", "panel", "--round", "1", "--lane", "fable", "--brief", str(e.brief))
    assert code == 0 and (e.repo / "docs" / "panels" / "09-22-t" / "ledger.md").is_file()   # the one folder the tool makes itself
    typo = e.repo / "docs" / "panels" / "09-22-typo"                # 2026-09-23 last look: collect and close made a mistyped panel folder; a bad brief or CLI left one
    assert run(e, "round", "collect", "--feature", "panels/09-22-typo", "--kind", "panel", "--round", "1", "--lane", "fable")[0] == 64
    assert run(e, "round", "close", "--feature", "panels/09-22-typo")[0] == 64
    assert run(e, "round", "prepare", "--feature", "panels/09-22-typo", "--kind", "panel", "--round", "1", "--lane", "fable", "--brief", str(e.tmp / "nope.md"))[0] == 64
    for bad in (["--file", str(e.tmp / "nope.md")], ["--head", "0" * 12], ["--kind", "design", "--head", e.head], ["--kind", "diff", "--head", e.head, "--base", e.base]):   # 2026-09-23 pre-review: a bad --file, --head or kind left one too; 0.1.9 last look F1: so did a diff round 1
        assert run(e, "round", "prepare", "--feature", "panels/09-22-typo", "--kind", "panel", "--round", "1", "--lane", "fable", "--brief", str(e.brief), *bad)[0] == 64
    (e.tmp / "gone.toml").write_text('[sol]\nmodel = "m"\neffort = "high"\ncommand = ["parsec-no-such-cli"]\n', encoding="utf-8")
    e.mp.setattr(parsec, "LANES_FILE", e.tmp / "gone.toml")
    code, out = run(e, "round", "run", "--feature", "panels/09-22-typo", "--kind", "panel", "--round", "1", "--lane", "sol", "--brief", str(e.brief))
    assert code == 64 and "not found on PATH" in out and not typo.exists()


# row 14b: an agent's confirming round resumes it by id (0.1.10 last look: agent confirming rounds were recorded as fresh; Q2 "A")
def test_agent_resume(env):
    e = env
    prep = lambda kind, n, *extra: run(e, "round", "prepare", "--feature", "09-22-x", "--kind", kind, "--round", str(n), "--lane", "fable",
                                       "--brief", str(e.brief), "--head", e.head, *(["--base", e.base] if kind != "design" else []), *extra)
    coll = lambda kind, n, reply, *extra: ((e.feat / "rounds" / f"{kind}-r{n}-fable" / "reply.md").write_text(reply, encoding="utf-8"),
                                          run(e, "round", "collect", "--feature", "09-22-x", "--kind", kind, "--round", str(n), "--lane", "fable", *extra))[1]
    assert prep("design", 1, "--resume", "a-1")[0] == 64 and not (e.feat / "rounds" / "design-r1-fable").exists()   # no earlier round to resume
    assert prep("design", 1)[0] == 0 and coll("design", 1, "VERDICT: FIX\n", "--agent-id", "a-1")[0] == 0
    assert e.record("design", 1, "fable")["session"] == "a-1"                    # spec review, Q3 "a": round 1 records the agent it ran on
    for bad in (["--resume", "a-2"], ["--resume", "a-1", "--fresh"]):            # another agent, or a resume that is also fresh
        assert prep("design", 2, *bad)[0] == 64 and not (e.feat / "rounds" / "design-r2-fable").exists()
    assert prep("design", 2, "--resume", "a-1")[0] == 0
    pend = json.loads((e.feat / "rounds" / "design-r2-fable" / "pending.json").read_text(encoding="utf-8"))
    assert pend["resumed"] is True and pend["session"] == "a-1"
    reply = "CONTINUITY: FIX, F1 the ledger point\n\nVERDICT: PASS\n"
    assert coll("design", 2, reply, "--agent-id", "a-2")[0] == 64 and (e.feat / "rounds" / "design-r2-fable" / "pending.json").is_file()   # not the agent prepare named
    code, out = coll("design", 2, reply, "--ran-ms", "459129")                 # Brandon Q2 A, 2026-10-21: the notification's duration_ms is the run, not the wait since prepare
    assert code == 0 and blk(out).endswith("### 🟢 Fable R2 Design Round: PASS (8 min, resumed)\n")
    r = e.record("design", 2, "fable")
    assert r["session"] == "a-1" and r["continuity"] == "FIX, F1 the ledger point" and "design r2 fable: PASS, continuity answered" in e.ledger().splitlines()[-1] and r["seconds"] == 459
    assert prep("design", 3)[0] == 0 and json.loads((e.feat / "rounds" / "design-r3-fable" / "pending.json").read_text(encoding="utf-8"))["resumed"] is False   # design r1 F1: no --resume, no resume
    assert prep("lastlook", 1)[0] == 0 and coll("lastlook", 1, "VERDICT: FIX\n")[0] == 0   # collected without the id: session unknown, as before
    assert e.record("lastlook", 1, "fable")["session"] == "unknown" and prep("lastlook", 2, "--resume", "z-9")[0] == 0   # so this one resume goes unchecked
    code, out = run(e, "round", "run", "--feature", "09-22-x", "--kind", "design", "--round", "1", "--lane", "sol", "--brief", str(e.brief), "--head", e.head, "--resume", "a-1")
    assert code == 2                                                              # round run has no --resume


# row 14c: a reason reaches a ledger line; past 130 characters the parser refuses it (Sol design r1 F2; Brandon, 2026-09-23: "B1"; 09-23-review-briefs amendment 1's reason was about 150)
def test_reason_cap(env):
    e = env
    before = e.ledger()
    for args in (["verify", "--feature", "09-22-x", "--record-amendment"],
                 ["round", "collect", "--feature", "09-22-x", "--kind", "design", "--round", "1", "--lane", "fable", "--degraded"],
                 ["round", "collect", "--feature", "09-22-x", "--kind", "design", "--round", "1", "--lane", "fable", "--close-minor"]):
        assert run(e, *args, "x" * 131)[0] == 2                                  # refused by the parser, before any command body
    assert e.ledger() == before and not (e.feat / "rounds").exists()           # so nothing is written
    assert run(e, "verify", "--feature", "09-22-x", "--record-amendment", "x" * 130)[0] == 64   # 130 reaches verify, which refuses only for want of a design PASS


# row 14d: the tool prints the summary's opening lines (2026-09-23 KitnEssentials phase 6 on 0.1.11 posted a prose summary: no marker, counts or bullets)
def test_summary_head(env):
    e = env
    e.mp.setenv("FAKE_REPLY", "- F2 · Important: 3 of 20 lack it.\nTrigger: a reload\n\nCritical 0, Important 1, Minor 2\n\nVERDICT: FIX\n")   # pre-review F1: printed Important 3
    assert run(e, "doctor", "--lane", "astra", "--kind", "design", "--feature", "09-22-x")[0] == 0   # 2026-10-04 Afterparty: 2 of 5 pre-flights and 4 of 18 summaries posted
    out = rnd(e, 1)[1]
    assert "\n\n### 🔴 Astra R1 Design Round: FIX (0 min, fresh)\n\nCritical 0 · Important 1 · Minor 2\n\n🟢 Pre-flight (" in out, out
    assert "· Model gpt" in out and not (e.feat / "rounds" / "preflight-astra.txt").exists()   # the green pre-flight rides once, in the lane's next summary
    e.mp.setenv("FAKE_REPLY", "**0 Critical, 0 Important, 3 Minor.**\n\nVERDICT: PASS\n")
    out = rnd(e, 2)[1]
    assert "\n### 🟢 Astra R2 Design Round: PASS (0 min, resumed)\n\nCritical 0 · Important 0 · Minor 3\n" in out and "Pre-flight" not in out
    e.mp.setenv("FAKE_REPLY", "Critical: 0\nImportant: 1\nMinor: 2\n\nVERDICT: PASS\n")   # pre-review F1: printed 0, 0, 1; no one line holds all three
    assert blk(rnd(e, 3)[1]).endswith("### 🟢 Astra R3 Design Round: PASS (0 min, resumed)\n")
    run(e, "round", "prepare", "--feature", "09-22-x", "--kind", "design", "--round", "1", "--lane", "fable", "--brief", str(e.brief), "--head", e.head)
    (e.feat / "rounds" / "design-r1-fable" / "reply.md").write_text("VERDICT: FIX\n", encoding="utf-8")
    out = run(e, "round", "collect", "--feature", "09-22-x", "--kind", "design", "--round", "1", "--lane", "fable")[1]
    assert blk(out).endswith("### 🔴 Fable R1 Design Round: FIX (0 min since prepare, fresh)\n") and "warning: the reply has no counts line" in out   # pre-review F2: an agent round gets its minutes too; field audit 4: "185 min, fresh" read as review time


# row 14e: the whole summary block, one bullet per finding (2026-09-25 audit: the heading alone was pasted in about a third of rounds)
def test_summary_bullets(env):
    e = env
    ask = "\n\n  → **Answer:** pending"
    e.mp.setenv("FAKE_REPLY", "### F1 (Important, new): the hold is lost.\nTrigger: a reload\n- **M2 · Minor — wording.**\nC1: holds\n\nCritical 0 · Important 1 · Minor 1\n\nVERDICT: FIX\n")
    out = rnd(e, 1)[1]
    assert blk(out).endswith("Critical 0 · Important 1 · Minor 1\n\n- **F1 · Important:** the hold is lost." + ask + "\n\n- **M2 · Minor:** wording." + ask + "\n"), out
    e.mp.setenv("FAKE_REPLY", "- **M1.** no grade\n\nCritical 0 · Important 0 · Minor 1\n\nVERDICT: PASS\n")   # four shapes in five replies (Fable poll): no ID guessed
    out = rnd(e, 2)[1]
    assert "warning: the reply's finding lines do not match its counts line" in out and blk(out).endswith("- **? · Minor:** not parsed, see rounds\\design-r2-astra\\reply.md" + ask + "\n")
    e.mp.setenv("FAKE_REPLY", "VERDICT: PASS\n\nlater draft text\n")
    assert "the reply's last line is not a VERDICT line with one verdict word" in rnd(e, 3)[1]   # and the next round 3 below reruns it under its number
    e.mp.setenv("FAKE_REPLY", "- M1 · Minor: wording.\n- I1 · Important: the hold is lost.\n  Trigger: a reload\n\nCritical 0 · Important 1 · Minor 1\n\nVERDICT: FIX\n")   # 0.1.15 last look F1: a Minor first in the reply
    out = rnd(e, 3)[1]
    assert out.index("- **I1 · Important:**") < out.index("- **M1 · Minor:**"), out
    span = "see `" + "long " * 30 + "code` end"                        # 2026-09-28 audit: gk-4, gk-5, gk-7 bullets broke their Markdown
    e.mp.setenv("FAKE_REPLY", f"F1 · Minor: `KE:Hide` is gone when\nthe frame hides\nF2 · Minor: {span}\nOpus F1 (the fake): `ride`\n\nCritical 0 · Important 0 · Minor 3\n\nVERDICT: PASS\n")
    out = rnd(e, 4)[1]
    assert "- **F1 · Minor:** `KE:Hide` is gone when …" + ask in out and "long …`" + ask in out and blk(out).endswith("- **? · Minor:** not parsed, see rounds\\design-r4-astra\\reply.md" + ask + "\n"), out   # a carried Minor: parsed rows stay; 2026-10-04 Afterparty: summaries.md kept blank ? bullets
    assert (e.feat / "summaries.md").read_text(encoding="utf-8").endswith(blk(out)[out.index("### 🟢 Astra R4"):].replace(parsec.PENDING, "").rstrip() + "\n\n")   # decision 1a: the finish report's file; pre-review F4: no "pending"
    (e.feat / "rounds" / "design-r1-astra" / "reply.md").write_text("the author's answer\n", encoding="utf-8")   # 2026-09-26 gk-1
    out = rnd(e, 5)[1]
    assert "design-r1-astra" in out and "changed after its round was collected" in out and "design-r3-astra.dead" not in out   # a dead round's reply is its own
    e.mp.setenv("FAKE_REPLY", "- Opus F2 · Minor: carried: ride, wording\n- Opus F3 / Sol F1 · Minor: twice\n- api-validator 2 · Minor: no ID\n"
                "- Sol R3 F1 / Astra R3 F2 · Minor: lanes\n- api-validator t2-7 1 · Minor: tasks\n- api-validator r2-M1 · Minor: round\n\nThe round 1 Important findings are closed.\nround-api 2 · Minor: x\nThere are 2 Important findings, I found 3 Minor ones.\n"   # field audit 4: about 87 ? bullets in 24 gate blocks; Kimi F1: a hyphenated label never starts "round-"
                "- F9 · Minor (carried: Opus F2, Sol F1): kept\n### FabF1 · Minor · own\n\nCritical 0 · Important 0 · Minor 8\n\nVERDICT: PASS\n")   # 2026-10-04 to 10-06 Afterparty: carried Minors in these shapes were ? bullets
    out = rnd(e, 6)[1]
    assert "do not match" not in out and all(f"- **{i} · Minor:** {t}" in out for i, t in (("Opus F2", "carried: ride, wording"), ("Opus F3 / Sol F1", "twice"), ("api-validator 2", "no ID"), ("FabF1", "own"),
                                                                                         ("Sol R3 F1 / Astra R3 F2", "lanes"), ("api-validator t2-7 1", "tasks"), ("api-validator r2-M1", "round"), ("F9", "kept"))), out


# row 14g: a Critical or Important finding with no Trigger: line counts as Minor (2026-11-22, atrocityUI cn-10: rounds paid for guards against cases nothing reaches, 33 of 71 cut)
def test_regrade_without_trigger(env):
    e = env
    e.mp.setenv("FAKE_REPLY", "Trigger: above every finding\n- F1 · Important: kept.\n  **Trigger:** a reload\n- F2 · Important: no trigger. Trigger: inline\nF3 · Critical: lost.\n- F4 · Minor: wording.\n"
                "  Trigger: under the Minor\n- F5 · Important: beside an unparsed one.\n- **M1.** no grade\n  Trigger: under M1\n\nCritical 1 · Important 3 · Minor 2\n\nVERDICT: FIX\n")   # design look r1 F1 (Brandon, Q13): a trigger in the finding's block holds it, an unparsed item's included; above every finding or inside the line, none
    out = rnd(e, 1)[1]
    assert "warning: F2 is graded Important with no Trigger: line under it, so it counts as Minor (templates/brief.md, Rules)" in out and "warning: F3 is graded Critical" in out and "stands after" not in out, out
    assert "Critical 0 · Important 2 · Minor 4 (regraded to Minor, no Trigger line: F2, F3)\n\n- **F1 · Important:** kept." in out and "- **F5 · Important:** beside an unparsed one." in out and "- **F3 · Minor (was Critical, no Trigger line):** lost." in out and "- **F4 · Minor:** wording." in out and "- **? · Minor:** not parsed" in out, out
    assert e.record("design", 1, "astra")["regraded"] == ["F2 Important", "F3 Critical"] and ", regraded to Minor: F2, F3, rounds" in e.ledger().splitlines()[-1] and "Critical 1 · Important 3 · Minor 2" in (e.feat / "rounds" / "design-r1-astra" / "reply.md").read_text(encoding="utf-8")
    e.mp.setenv("FAKE_REPLY", "### F1 · Important: the hold is lost.\n\nCritical 0 · Important 1 · Minor 0\n\nVERDICT: FIX\n")   # the verdict stays the reviewer's; the close-on-Minor path ends it
    out = rnd(e, 2)[1]
    assert "### 🔴 Astra R2 Design Round: FIX" in out and "Critical 0 · Important 0 · Minor 1 (regraded to Minor, no Trigger line: F1)" in out and "do not match" not in out and "warning: no Critical or Important finding stands after the regrade: the FIX closes on Minor once each finding is answered (round collect --close-minor)" in out, out
    assert run(e, "round", "collect", "--feature", "09-22-x", "--kind", "design", "--round", "2", "--lane", "astra", "--close-minor", "regraded")[0] == 0 and run(e, "verify", "--feature", "09-22-x")[1].strip() == "MATCH (CLOSED ON MINOR)"
    e.mp.setenv("FAKE_REPLY", "- F1 · Important: listed first.\n- F2 · Minor: wording.\n\n### F1 · Important: listed first\n- Trigger: a reload\n### F3 · Important: bold after\n**Trigger**: x\n• F4 · Important: kimi\n• Trigger: x\n### F5 · Important: heading\n\n### Trigger: x\n"
                "F6 · Important: upper\nTRIGGER: x\n### F7 · Important: no mark\ntrigger: lower case\nF8 · Important: a title the reviewer\nhard-wrapped here\nTrigger: x\n"
                "F9 · Important: the record is written before `regraded`\nis added to it\nTrigger: x\nF10 · Important: a title whose rest\nStarts in capitals\nTrigger: x\nF11 · Important: a title on\nthree lines, as the reviewer\nwrapped it twice\nTrigger: x\n"
                "F12 · Important: numbered\n1. Trigger: x\nF13 · Important: plus\n+ Trigger: x\nF14 · Important: code\n`Trigger:` x\nF15 · Important: underscored\n_Trigger:_ x\nF16 · Important: numbered bold\n1) **Trigger:** x\nF17 · Important: the hold is lost\n```lua\nlocal x\n```\nbecause the frame hides it\nTrigger: x\n\nCritical 0 · Important 16 · Minor 1\n\nVERDICT: PASS\n")   # design r1 F4, F10: every form, a title the trigger leaves whole, a wrapped title; design look r1 F1: the wraps the … test does not see; pre-review r1 F1: the list, code and underscore shapes; F3: a fence is no title's rest
    out = rnd(e, 3)[1]
    assert "### 🟢 Astra R3 Design Round: PASS" in out and "Critical 0 · Important 16 · Minor 1\n\n- **F1 · Important:** listed first." in out and "- **F7 · Important:** no mark\n" in out and "- **F8 · Important:** a title the reviewer …" in out and "- **F17 · Important:** the hold is lost\n" in out and e.record("design", 3, "astra")["regraded"] == [], out
    e.mp.setenv("FAKE_REPLY", "Opus F2 · Important: carried.\n### F3 · Important: fenced.\n```\nTrigger: in a fence\nF12 · Important: a fenced example\n```\n### F9 · Important: late\n\nA first paragraph.\n\nTrigger: after it\nF10 · Important: quoted\n> Trigger: quoted\n"   # diff r1 F3: an ID of its own, so a counted example removes the ? row, and the trigger above it, so a read one holds F3
                "### F11 · Important: a heading, then an unparsed item\n- **M2.** no grade\n  Trigger: under M2\n\nCritical 0 · Important 6 · Minor 0\n\nVERDICT: FIX\n")   # design r2 F2, F4: a fence (a finding line in it too) and a quote give none; Q13: a later line and an unparsed item's trigger hold; a ? keeps its grade and the FIX open
    out = rnd(e, 4)[1]
    assert "Critical 0 · Important 3 · Minor 3 (regraded to Minor, no Trigger line: Opus F2, F3, F10)" in out and "- **? · Important:** not parsed" in out and "stands after" not in out, out
    e.mp.setenv("FAKE_REPLY", "- F1 · Important: one.\n- F2 · Important: two.\n\nCritical 0 · Important 1 · Minor 0\n\nVERDICT: FIX\n")   # more finding lines than the counts line: nothing regraded, a ? keeps its grade
    out = rnd(e, 5)[1]
    assert "Critical 0 · Important 1 · Minor 0\n\n- **? · Important:** not parsed" in out and "regraded" not in out and "do not match its counts line" in out, out
    e.mp.setenv("FAKE_REPLY", "- F1 · Important: no trigger.\n\nCritical 0 · Important 1 · Minor 0\n\nVERDICT: PASS\n")   # design r3 F19: a PASS is regraded too, its verdict and marker kept
    code, out = rnd(e, 6)
    assert code == 0 and "### 🟢 Astra R6 Design Round: PASS" in out and "Critical 0 · Important 0 · Minor 1 (regraded to Minor, no Trigger line: F1)" in out and "stands after" not in out and e.record("design", 6, "astra")["regraded"] == ["F1 Important"], out
    e.mp.setenv("FAKE_REPLY", "- **F1.** Settings fail to load (Important)\n  Trigger: a reload\n\n> F9 · Important: an earlier example\n- > F8 · Important: a quote in a list item\n\nCritical 0 · Important 1 · Minor 0\n\nVERDICT: FIX\n")   # design r4 F22 (Brandon, Q11): a quoted example must not take the real Important's count; pre-review r1 F2: nor one quoted inside a list item
    out = rnd(e, 7)[1]
    assert "Critical 0 · Important 1 · Minor 0\n\n- **? · Important:** not parsed" in out and "F9" not in out and "F8" not in out and "regraded" not in out and "stands after" not in out, out
    e.mp.setenv("FAKE_REPLY", "- F1 · Important: no trigger.\n\nVERDICT: FIX\n")   # diff r1 F3: with no counts line, a finding with no trigger is not regraded
    assert "no counts line" in (out := rnd(e, 8)[1]) and "regraded" not in out and "stands after" not in out and e.record("design", 8, "astra")["regraded"] == [], out
    for kind, rest in (("panel", []), ("lastlook", ["--head", e.head, "--base", e.base])):   # a panel's FIX judges options; a last look's PASS comes from its one confirming question (design r1 F5)
        run(e, "round", "prepare", "--feature", "09-22-x", "--kind", kind, "--round", "1", "--lane", "fable", "--brief", str(e.brief), *rest)
        (e.feat / "rounds" / f"{kind}-r1-fable" / "reply.md").write_text("F1 · Important: no trigger.\n\nCritical 0 · Important 1 · Minor 0\n\nVERDICT: FIX\n", encoding="utf-8")
        out = run(e, "round", "collect", "--feature", "09-22-x", "--kind", kind, "--round", "1", "--lane", "fable")[1]
        assert "Critical 0 · Important 0 · Minor 1 (regraded to Minor, no Trigger line: F1)" in out and "closes on Minor" not in out and ("stands after" in out) == ("ask the one confirming question for the PASS" in out) == (kind == "lastlook"), out   # diff r1 F3: a panel prints no close warning of any text
    ll = lambda lane, n, reply, *extra: (run(e, "round", "prepare", "--feature", "09-22-x", "--kind", "lastlook", "--round", str(n), "--lane", lane, "--brief", str(e.brief), "--head", e.head, "--base", e.base, *extra),
                                         (e.feat / "rounds" / f"lastlook-r{n}-{lane}" / "reply.md").write_text(reply, encoding="utf-8"), run(e, "round", "collect", "--feature", "09-22-x", "--kind", "lastlook", "--round", str(n), "--lane", lane)[1])[2]
    fix = "F1 · Important: no trigger.\n\nCritical 0 · Important 1 · Minor 0\n\nVERDICT: FIX\n"
    assert "verdict: NONE" in ll("opus", 1, "F1 · Important: no trigger.\n")   # design r5 F25: an interrupted first look, rerun on its session under its own number, is still the first look
    out = ll("opus", 1, fix, "--resume", "z-9")
    assert "ask the one confirming question for the PASS" in out and "goes to Brandon" not in out, out
    assert "verdict: NONE" in ll("opus", 2, "F1 · Important: no trigger.\n")   # design r6 F25: a fresh look on a new head after the z-9 look's verdict, cut off, then rerun on its own agent
    out = ll("opus", 2, fix, "--resume", "y-1")
    assert "ask the one confirming question for the PASS" in out and "goes to Brandon" not in out, out
    out = ll("fable", 2, fix, "--resume", "z-9") + ll("opus", 3, "F1 · Important: no trigger.\n", "--resume", "y-1") + ll("opus", 3, fix, "--resume", "y-1")   # design r3 F18: the confirming question itself, after the look's recorded FIX: on an unknown session, and (design look r1 F2) on the session the look recorded, (diff r1 F3) retried after a NONE
    assert out.count("warning: no Critical or Important finding stands after the regrade: this FIX answers the one confirming question, and a second FIX goes to Brandon") == 2 and "ask the one confirming question for the PASS" not in out, out


# row 14f: what the brief names reaches the package (2026-09-28 audit: notes.md and a canvas file no package held; gate logs in 4 of 16 phases)
def test_named_evidence(env):
    e = env
    (e.feat / "notes.md").write_text("# Notes\n", encoding="utf-8")
    (e.repo / ".claude-plugin").mkdir()                              # 0.1.20 last look: a bare name that lives in a subfolder warned
    (e.repo / ".claude-plugin" / "plugin.json").write_text("{}\n", encoding="utf-8")
    git("add", ".claude-plugin", cwd=e.repo)
    git("commit", "-qm", "plugin", cwd=e.repo)
    e.head = git("rev-parse", "HEAD", cwd=e.repo)
    (e.feat / "gate-zero.md").write_text("# Gate zero\n", encoding="utf-8")   # 2026-10-04 Afterparty ap-13: 27 rounds named a feature-folder file no package held
    e.brief.write_text("Read `notes.md` beside the spec, `AGENTS.md:3`, `plugin.json`, `ghost.json`, `gate-zero.md` and `pages/canvas.json`.\n", encoding="utf-8")
    out = rnd(e, 1)[1]
    ctx = (e.wt / "_review" / "proj-09-22-x-design-astra" / ".parsec" / "context.md").read_text(encoding="utf-8")
    assert "- notes: .parsec/notes.md, the brainstorm record" in ctx and out.count("the brief names") == 2 and "names pages/canvas.json" in out and "names ghost.json" in out, out
    assert out.index("names ghost.json") < out.index("verdict:") and out.endswith("before any other step; 5 warning(s) above the block\n")   # field audit 4: printed only after the lane finished; a sed from ### dropped the post line
    assert "- evidence: .parsec/evidence/1-gate-zero.md is a copy of gate-zero.md" in ctx and "packed gate-zero.md from the feature folder" in out
    (e.feat / "rounds" / "answers.md").write_text("a\n", encoding="utf-8")   # pre-review F1, F2: the path as named, inside the feature folder only
    e.brief.write_text("Read `gate-zero.md`, `../other/gate-zero.md` and `rounds/answers.md`.\n", encoding="utf-8")
    out = rnd(e, 1, "sol", "diff")[1]
    ctx = (e.wt / "_review" / "proj-09-22-x-diff-sol" / ".parsec" / "context.md").read_text(encoding="utf-8")
    assert "names ../other/gate-zero.md" in out and "1-gate-zero.md" in ctx and "2-answers.md" in ctx and "no --file named like a gate log" in out, out   # F4: packed files are no gate log
    e.brief.write_text("Read `notes.md`, the earlier `reply.md` and `pages/canvas.json`.\n", encoding="utf-8")   # pre-review F1, Sol diff r1 F2: a passed file is found by its name
    (e.tmp / "canvas.json").write_text("{}", encoding="utf-8")
    assert "the brief names" not in rnd(e, 2, "astra", "design", "--file", str(e.tmp / "canvas.json"))[1]
    assert "no --file named like a gate log" in rnd(e, 2, "sol", "diff")[1]
    for name in ("gate-log.txt", "latest-checkout-checksums.md"):            # field audit 4: Moving Day phase 7's smoke and AceGUI files kept the warning silent; pre-review F5: so did a word holding "test"; Sol F1: and "checksums"
        (e.tmp / name).write_text("busted: 9 passed\n", encoding="utf-8")
    assert "like a gate log" in rnd(e, 3, "sol", "diff", "--file", str(e.tmp / "latest-checkout-checksums.md"))[1] and "like a gate log" not in rnd(e, 4, "sol", "diff", "--file", str(e.tmp / "gate-log.txt"))[1]


# row 14g: the Muse pre-flight and doctor row; Muse has no login status command, so auth.json's presence (2026-10-12)
def test_muse_preflight_and_doctor(env):
    e = env
    e.mp.setenv("FAKE_ENV_DUMP", str(e.tmp / "env.json"))
    e.mp.setenv("META_API_KEY", "stray-key")
    code, out = run(e, "doctor", "--lane", "muse", "--kind", "design", "--feature", "09-22-x")
    assert code == 64 and out.startswith("### 🔴 Pre-flight: Muse · design debate · FAILED") and "- **CLI:** fake-cli 1.0, auth.json MISSING" in out, out
    child = json.loads((e.tmp / "env.json").read_text(encoding="utf-8"))
    assert child["MUSE_NO_AUTO_UPDATE"] == "1" and "META_API_KEY" not in child   # 2026-10-12: a version call starts the launcher's update check
    row = [l for l in run(e, "doctor")[1].splitlines() if l.endswith(": muse (muse-wonder-full-1.0, high)")]
    assert row == ["- 🔴 fake-cli 1.0, auth.json MISSING: muse (muse-wonder-full-1.0, high)"], row
    child = json.loads((e.tmp / "env.json").read_text(encoding="utf-8"))   # the table's last call is muse's version call
    assert child["MUSE_NO_AUTO_UPDATE"] == "1" and "META_API_KEY" not in child
    (e.home / ".config" / "muse").mkdir(parents=True)
    (e.home / ".config" / "muse" / "auth.json").write_text("{}", encoding="utf-8")
    code, out = run(e, "doctor", "--lane", "muse", "--kind", "design", "--feature", "09-22-x")
    assert code == 0 and "- **CLI:** fake-cli 1.0, auth.json present\n- **Model:** muse-wonder-full-1.0, effort high (lanes.toml), contributor mode off" in out, out
    assert "\n- 🟢 fake-cli 1.0, auth.json present: muse (muse-wonder-full-1.0, high)\n" in run(e, "doctor")[1]


# row 14h: the Neon pre-flight, its child environment and the one agy doctor row (2026-11-20 C5: agy models names the id; C6: it lists models with no login check; design round 1)
def test_neon_preflight_and_doctor(env):
    e = env
    pf, dump = lambda lane="neon": run(e, "doctor", "--lane", lane, "--kind", "design", "--feature", "09-22-x"), lambda: json.loads((e.tmp / "env.json").read_text(encoding="utf-8"))
    for k, v in (("FAKE_STDOUT", "  gemini-4-neon-high\tindented\ngemini-4-neon-high-preview\tGemini 4 Neon preview\ngemini-4-neon-high\n"), ("FAKE_STDERR", "gemini-4-neon-high\tGemini 4 Neon (High)\n"), ("FAKE_ENV_DUMP", str(e.tmp / "env.json")), ("GEMINI_API_KEY", "stray-key")): e.mp.setenv(k, v)   # an indented row, a longer id, the id alone, or the id on standard error, is no row (Sol F7, Astra F9, F29)
    code, out = pf(); assert code == 64 and out.startswith("### 🔴 Pre-flight: Neon · design debate · FAILED") and "model gemini-4-neon-high is not in agy models" in out and "- **CLI:** agy fake-cli 1.0, model NOT KNOWN to agy" in out, out
    e.mp.setenv("FAKE_STDOUT", "gemini-4-hydrogen-high\tGemini 4 Hydrogen (High)\ngemini-4-neon-high\tGemini 4 Neon (High)\n"); e.mp.setenv("FAKE_EXIT", "1"); assert (r := pf())[0] == 64 and "agy models failed (exit 1)" in r[1] and "is not in agy models" not in r[1] and "model not checked (agy models failed)" in r[1], r[1]; e.mp.delenv("FAKE_EXIT")   # the row printed, then a failed exit (Astra F37)
    code, out = pf()
    assert code == 0 and ["models"] in e.calls() and "GEMINI_API_KEY" not in dump() and "- **CLI:** agy fake-cli 1.0, model known to agy\n- **Model:** gemini-4-neon-high, effort high (lanes.toml; the id picks the level); login not checked (C6: no logged-out run was possible)" in out, out   # the dump is agy models'; the version call's own environment is untested, accepted residual R1 (Brandon, 2026-11-20)
    e.mp.setenv("FAKE_VERSION_EXIT", "3"); assert (r := pf())[0] == 64 and r[1].startswith("### 🔴 Pre-flight: Neon · design debate · FAILED") and "model known to agy" in r[1], r[1]; e.mp.delenv("FAKE_VERSION_EXIT")   # a failed version call fails the pre-flight with the model listed (Sol R4 F2, Astra F28)
    rows = parsec.tomllib.loads((REPO / "lanes.toml").read_text(encoding="utf-8")); assert "gemini" not in rows and [k for k, r in rows.items() if r.get("command") == ["agy"]] == ["neon"]   # the shipped rows: neon alone runs agy (direct build, 2026-11-25)
    cmd, upd = json.dumps([sys.executable, str(FAKE)]), json.dumps([sys.executable, str(FAKE), "update", "agy"])
    (e.tmp / "lanes.toml").write_text(f'[neon]\nmodel = "gemini-4-neon-high"\neffort = "high"\ncommand = {cmd}\nupdate = {upd}\n', encoding="utf-8")
    code, out = run(e, "doctor", "--update")
    assert "\n- 🟢 fake-cli 1.0, login in the first run's log: neon (gemini-4-neon-high, high)\n" in out and [c for c in e.calls() if c[:1] == ["update"]] == [["update"], ["update", "agy"]] and "- **update neon:** exit 0" in out, out   # the row's order no longer sends agy to the Kimi credentials check


# row 16: the Gemini build path is gone (2026-11-25 direct-build trial: the session builds from the spec; Brandon D1-A); its commands exit 2, its lane 64
def test_removed_build_path(env, capsys):
    e = env
    for args, word in ((["task-brief", "--feature", "09-22-x", "--task", "1"], "task-brief"), (["build", "run", "--feature", "09-22-x", "--task", "1", "--checkout", ".", "--head", "HEAD"], "build"),
                       (["build", "archive", "--feature", "09-22-x", "--task", "1"], "build"), (["doctor", "--lane", "opus", "--kind", "build", "--feature", "09-22-x"], "build")):   # Sol diff r1 F2: no build pre-flight
        capsys.readouterr(); assert run(e, *args)[0] == 2 and f"invalid choice: '{word}'" in capsys.readouterr().err, args
    code, out = run(e, "doctor", "--lane", "gemini", "--kind", "design", "--feature", "09-22-x")
    assert code == 64 and "lane gemini is not a lane or a seat" in out, out

# row 17: fast mode, the tier read back from codex's session record (2026-09-22 fast_mode_probe2.py)
def test_tier_readback(env):
    e = env
    rnd(e, 1)
    assert e.record("design", 1, "astra")["tier_check"] == "unverified"
    roll = e.home / ".codex" / "sessions" / "2026" / "rollout-2026-09-22T00-00-00-01a0c9a2-0000-4000-8000-000000000001.jsonl"
    roll.write_text('{"type":"thread_settings_applied","payload":{"service_tier":"default"}}\n', encoding="utf-8")
    rnd(e, 2)
    r = e.record("design", 2, "astra")
    assert r["tier"] == "default" and r["tier_check"] == "verified"
    roll.write_text('{"type":"thread_settings_applied","payload":{"service_tier":"priority"}}\n', encoding="utf-8")
    code, out = rnd(e, 3)
    r = e.record("design", 3, "astra")
    assert r["tier"] == "priority" and r["tier_check"] == "unrequested" and "tier read-back priority differs" in out
    code, out = rnd(e, 4, "astra", "design", "--fast")
    assert e.record("design", 4, "astra")["tier_check"] == "verified" and e.record("design", 4, "astra")["tier"] == "fast"
    assert "service_tier=priority" in e.calls()[-1] and "tier: fast" in e.ledger().splitlines()[-1] and "tier: fast" not in e.ledger().splitlines()[-2]
