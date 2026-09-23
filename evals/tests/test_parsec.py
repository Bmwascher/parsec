"""Tests for tools/parsec.py, each standing on a recorded failure (step 5 of the rethink, rows 1 to 17).
The fake CLI is evals/tests/fake_cli.py; no model call, no network. Rows that need junctions or
taskkill run on Windows only."""
import importlib.util
import json
import os
import stat
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
FAKE = Path(__file__).with_name("fake_cli.py")
spec = importlib.util.spec_from_file_location("parsec", REPO / "tools" / "parsec.py")
parsec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parsec)
WIN = os.name == "nt"
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
    (feat / "tasks.md").write_bytes(b"# Plan\n\nheader line\n\n## Global constraints\n\n- keep it\n\n## File map\n\n- a\n\n"
                                    b"## Task 1: first\n\n- [ ] step\n\n```lua\nlocal x = 1\n```\n\n## Task 2: second\n\n- [ ] other\n")
    (feat / "ledger.md").write_text("# Ledger\n\n", encoding="utf-8")
    brief = tmp_path / "brief.md"
    brief.write_bytes(TRICKY.encode("utf-8"))
    lanes = tmp_path / "lanes.toml"
    cmd = json.dumps([sys.executable, str(FAKE)])
    lanes.write_text(f'[astra]\nmodel = "gpt-6-astra"\neffort = "high"\ncommand = {cmd}\n'
                     f'[sol]\nmodel = "gpt-5.6-sol"\neffort = "high"\ncommand = {cmd}\n'
                     f'[kimi]\nmodel = "kimi-code/k3"\ncommand = {cmd}\nhome = "{(tmp_path / "kimi-home").as_posix()}"\n'
                     f'[gemini]\nmodel = "gemini-3.8-flash-high"\ncommand = {cmd}\n', encoding="utf-8")
    (tmp_path / "kimi-home").mkdir()
    (tmp_path / "kimi-home" / "config.toml").write_text('[models."kimi-code/k3"]\ndefault_effort = "high"\n', encoding="utf-8")
    monkeypatch.setattr(parsec, "LANES_FILE", lanes)
    monkeypatch.setattr(parsec, "POLL_SECONDS", 0.05)
    log = tmp_path / "calls.jsonl"
    monkeypatch.setenv("FAKE_LOG", str(log))
    monkeypatch.setenv("FAKE_STDOUT", "OpenAI Codex v9.9.9\n--------\nsession id: 01a0c9a2-0000-4000-8000-000000000001\n--------\n")
    monkeypatch.setenv("FAKE_REPLY", "Summary.\n\nVERDICT: FIX\n")
    for k in ("FAKE_EXIT", "FAKE_SLEEP", "FAKE_WRITE", "FAKE_STDERR", "FAKE_STDIN_COPY", "FAKE_ENV_DUMP", "FAKE_CHILD_PID_FILE"):
        monkeypatch.delenv(k, raising=False)

    class E:
        pass
    e = E()
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


# row 1: codex argument list, on round 1 and on resume; 2026-07-24, 07-28, 08-11, 09-22 (the inherited tier)
def test_codex_flags_before_resume(env):
    e = env
    code, out = rnd(e, 1)
    assert code == 0, out
    fresh = e.calls()[-1]
    pairs = list(zip(fresh, fresh[1:]))
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
    child = json.loads((e.tmp / "env.json").read_text(encoding="utf-8"))
    assert child["KIMI_CODE_HOME"] == str(e.tmp / "kimi-home")
    assert e.record("design", 1, "kimi")["session"] == "session_2fc45d80-9dc5-4b9b-9561-65f39c787383"
    code, out = rnd(e, 2, "kimi")
    a = e.calls()[-1]
    assert "--agent-file" not in a and a[a.index("--session") + 1] == "session_2fc45d80-9dc5-4b9b-9561-65f39c787383"


# row 3: CODEX_HOME is absent from the codex child (2026-07-24)
def test_codex_home_removed(env):
    e = env
    e.mp.setenv("CODEX_HOME", str(e.tmp / "elsewhere"))
    e.mp.setenv("FAKE_ENV_DUMP", str(e.tmp / "env.json"))
    rnd(e, 1)
    child = json.loads((e.tmp / "env.json").read_text(encoding="utf-8"))
    assert "CODEX_HOME" not in child and child["NO_COLOR"] == "1"


# row 4: the brief reaches standard input byte for byte (2026-09-17; 2026-08-11)
def test_brief_bytes_reach_stdin(env):
    e = env
    e.mp.setenv("FAKE_STDIN_COPY", str(e.tmp / "stdin.bin"))
    rnd(e, 1)
    assert (e.tmp / "stdin.bin").read_bytes() == TRICKY.encode("utf-8")
    assert (e.feat / "rounds" / "design-r1-astra" / "brief.md").read_bytes() == TRICKY.encode("utf-8")
    assert e.record("design", 1, "astra")["brief_sha256"] == parsec.sha256(e.brief)


# row 5: resume by the recorded id, never --last; the rerun rule (2026-09-01; the scoping note's seven briefs)
def test_rerun_rule(env):
    e = env
    e.mp.setenv("FAKE_REPLY", "cut off before the verd")
    code, out = rnd(e, 1)
    assert code == 65 and e.record("design", 1, "astra")["verdict"] == "NONE"
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


# row 6: verdict reading (old items 34 and 67; the 2026-09-21 Kimi replies)
@pytest.mark.parametrize("text,want", [
    ("VERDICT: PASS\n", "PASS"), ("  - **VERDICT: FIX** - a sentence after\n", "FIX"), ("> VERDICT: ESCALATE\n", "ESCALATE"),
    ("VERDICT: BLIND\n", "BLIND"), ("end with VERDICT: PASS, FIX or ESCALATE\n", "NONE"), ("VERDICT: FAIL\n", "NONE"),
    ("VERDICT: PASS\nmore text and the reply was cut", "PASS"), ("no verdict line\n", "NONE"), ("VERDICT: PA", "NONE")])
def test_verdict_reading(text, want):
    assert parsec.verdict_of(text) == want


def test_continuity_and_wrote_files(env):
    e = env
    rnd(e, 1)
    e.mp.setenv("FAKE_REPLY", "CONTINUITY: FIX, the ledger point\n\nVERDICT: PASS\n")
    rnd(e, 2)
    r = e.record("design", 2, "astra")
    assert r["continuity"] == "FIX, the ledger point" and "continuity answered" in e.ledger().splitlines()[-1]
    e.mp.setenv("FAKE_REPLY", "VERDICT: PASS\n")
    rnd(e, 3)
    assert e.record("design", 3, "astra")["continuity"] is None and "continuity: not answered" in e.ledger().splitlines()[-1]
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
    assert r["verdict"] == "NONE" and r["cli_exit"] == 1 and r["brief_sha256"] == parsec.sha256(e.brief)
    assert "design r1 astra: NONE" in e.ledger()
    e.mp.setenv("FAKE_EXIT", "3")
    e.mp.setenv("FAKE_REPLY", "VERDICT: PASS\n")
    code, out = rnd(e, 1)
    assert code == 3
    code, out = run(e, "round", "run", "--feature", "nope", "--kind", "design", "--round", "1", "--lane", "astra",
                    "--brief", str(e.brief), "--head", e.head)
    assert code == 64


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
    (e.feat / "tasks.md").write_bytes((e.feat / "tasks.md").read_bytes() + b"\n## Task 3: fix\n\n- [ ] x\n")
    assert v()[1].strip() == "CHANGED"
    code, out = v("--record-amendment", "fix task for a gate finding")
    assert code == 0 and "amendment 1 recorded" in out and v()[1].strip() == "MATCH (DEGRADED PASS)"   # the flag carries
    assert (e.feat / "rounds" / "amendment-1.json").is_file()
    e.mp.setenv("FAKE_REPLY", "VERDICT: FIX\n")
    rnd(e, 3)
    assert v()[1].strip() == "NO-PASS-YET" and v("--record-amendment", "after an unclosed FIX")[0] == 64
    run(e, "round", "collect", "--feature", "09-22-x", "--kind", "design", "--round", "3", "--lane", "astra", "--close-minor", "wording")
    assert v()[1].strip() == "MATCH (CLOSED ON MINOR)"
    (e.feat / "spec.md").write_text("changed\n", encoding="utf-8")
    assert v()[1].strip() == "CHANGED"


# row 12: task-brief slices bytes (old item 113)
def test_task_brief_slice(env):
    e = env
    code, out = run(e, "task-brief", "--feature", "09-22-x", "--task", "1")
    path, digest = out.strip().splitlines()
    data = Path(path).read_bytes()
    assert path.endswith("task-01-brief.md") and digest == parsec.sha256(path)
    assert data.startswith(b"# Plan\n\nheader line\n\n") and b"## Global constraints\n\n- keep it\n\n" in data
    assert data.endswith(b"## Task 1: first\n\n- [ ] step\n\n```lua\nlocal x = 1\n```\n\n") and b"Task 2" not in data and b"File map" not in data
    assert run(e, "task-brief", "--feature", "09-22-x", "--task", "9")[0] == 64


# row 13: the doctor reads a stale install (old item 65)
def test_doctor_stale_install(env):
    e = env
    plug = e.home / ".claude" / "plugins"
    plug.mkdir(parents=True)
    plug.joinpath("installed_plugins.json").write_text(json.dumps(
        {"plugins": {"parsec@parsec": [{"version": "0.1.0", "gitCommitSha": "0" * 40}]}}), encoding="utf-8")
    e.mp.setattr(parsec, "PLUGIN", e.repo)
    code, out = run(e, "doctor")
    assert code == 0 and "STALE" in out and "bump it, then claude plugin update" in out   # 2026-09-22 17:16: update said "already latest"
    plug.joinpath("installed_plugins.json").write_text(json.dumps(
        {"plugins": {"parsec@parsec": [{"version": "0.1.0", "gitCommitSha": e.head}]}}), encoding="utf-8")
    assert "0.1.0 at " in run(e, "doctor")[1] and "STALE" not in run(e, "doctor")[1]
    cmd = json.dumps([sys.executable, str(FAKE)])
    upd = json.dumps([sys.executable, str(FAKE), "update"])
    (e.tmp / "lanes.toml").write_text(f'[astra]\nmodel = "a"\neffort = "high"\ncommand = {cmd}\nupdate = {upd}\n'
                                      f'[sol]\nmodel = "s"\neffort = "high"\ncommand = {cmd}\nupdate = {upd}\n'
                                      f'[gemini]\nmodel = "g"\ncommand = {cmd}\nupdate = {upd[:-1]}, "agy"]\n', encoding="utf-8")
    e.mp.setenv("FAKE_ENV_DUMP", str(e.tmp / "env.json"))
    code, out = run(e, "doctor", "--update")
    assert code == 0 and [c for c in e.calls() if c[:1] == ["update"]] == [["update"], ["update", "agy"]]   # 2026-09-22 review: codex updated twice
    assert json.loads((e.tmp / "env.json").read_text(encoding="utf-8"))["AGY_CLI_DISABLE_AUTO_UPDATE"] == "true"


# row 14: inputs, the pre-flight, the in-session package (old item 100; the 2026-09-21 dry run and Kimi login; "in this directory")
def test_inputs_and_preflight(env):
    e = env
    code, out = run(e, "round", "prepare", "--feature", "09-22-y", "--kind", "design", "--round", "1", "--lane", "opus",
                    "--brief", str(e.brief), "--head", e.head)
    assert code == 64 and not (e.repo / "docs" / "09-22-y").exists()
    code, out = run(e, "task-brief", "--feature", "../09-22-x", "--task", "1")
    assert code == 64 and "not under the docs root" in out      # 2026-09-22 review: --feature could climb out of the docs root
    (e.repo / ".claude" / "parsec.toml").rename(e.repo / ".claude" / "off.toml")
    code, out = run(e, "doctor", "--lane", "astra", "--kind", "design", "--feature", "09-22-x")
    assert code == 64 and "run setup first" in out
    assert run(e, "doctor")[0] == 64                            # 2026-09-22 review: the table printed "config:" and exited 0
    (e.repo / ".claude" / "off.toml").rename(e.repo / ".claude" / "parsec.toml")
    (e.repo / "AGENTS.md").rename(e.repo / "A.md")
    code, out = run(e, "doctor", "--lane", "astra", "--kind", "design", "--feature", "09-22-x")
    assert code == 64 and "rubric file not found" in out        # 2026-09-22 review: a missing rubric file only warned
    (e.repo / "A.md").rename(e.repo / "AGENTS.md")
    code, out = run(e, "doctor", "--lane", "astra", "--kind", "design", "--feature", "09-22-x")
    assert code == 0 and "2 of 2 sections found" in out and "tier default" in out, out
    assert "tier fast" in run(e, "doctor", "--lane", "astra", "--kind", "design", "--feature", "09-22-x", "--fast")[1]
    (e.repo / "AGENTS.md").write_text("# Rules\n\n## Lua style (renamed)\n\n## Git\n", encoding="utf-8")
    code, out = run(e, "doctor", "--lane", "astra", "--kind", "design", "--feature", "09-22-x")
    assert code == 64 and 'section not found: "Lua style"' in out and not (e.feat / "rounds").exists()
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
    assert code == 0 and "quota: 5 h 60% left" in out and time.time() - t0 < 8, out   # r4 (Sol): the reader returns at its first answer
    pid = (e.tmp / "quota.pid").read_text()
    assert not WIN or pid not in subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True).stdout   # r3 (Sol): the .CMD's child outlived the probe
    e.mp.delenv("FAKE_CHILD_PID_FILE")
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
    assert (folder / "pending.json").is_file() and not (e.wt / "_review").exists()
    (folder / "reply.md").write_text("report\n\nVERDICT: PASS\n", encoding="utf-8")
    code, out = run(e, "round", "collect", "--feature", "09-22-x", "--kind", "prereview", "--round", "1", "--lane", "opus")
    r = e.record("prereview", 1, "opus")
    assert code == 0 and r["verdict"] == "PASS" and r["agent"] == "reviewer-opus" and r["model"].startswith("claude-opus") and not (folder / "pending.json").exists()
    code, out = run(e, "round", "prepare", "--feature", "09-22-x", "--kind", "panel", "--round", "1", "--lane", "fable",
                    "--brief", str(e.brief), "--head", e.head, "--file", str(extra), "--file", str(extra))
    assert code == 64 and "twice" in out
    code, out = run(e, "round", "prepare", "--feature", "09-22-x", "--kind", "panel", "--round", "1", "--lane", "fable",
                    "--brief", str(e.brief))                   # 2026-09-22 16:45: two panel rounds died wanting a range
    assert code == 0 and e.head.startswith(json.loads((e.feat / "rounds" / "panel-r1-fable" / "pending.json").read_text(encoding="utf-8"))["head"])
    code, out = run(e, "round", "prepare", "--feature", "09-22-x", "--kind", "panel", "--round", "1", "--lane", "fable", "--brief", str(e.brief))
    assert code == 64 and "never collected" in out              # 2026-09-22: five Kimi rounds collided on one folder; the refusal held
    code, out = run(e, "round", "prepare", "--feature", "09-22-x", "--kind", "design", "--round", "9", "--lane", "fable", "--brief", str(e.brief))
    assert code == 64 and "--head is required" in out
    assert run(e, "round", "prepare", "--feature", "09-22-x", "--kind", "design", "--round", "9", "--brief", str(e.brief), "--head", e.head)[0] == 2
    conf = e.repo / ".claude" / "parsec.toml"
    conf.write_text(conf.read_text(encoding="utf-8") + '[reviewer]\ncodex_lane = "astra"\n', encoding="utf-8")
    code, out = run(e, "round", "run", "--feature", "09-22-x", "--kind", "design", "--round", "1", "--brief", str(e.brief), "--head", e.head)
    assert code == 0 and e.record("design", 1, "astra")["lane"] == "astra"   # 2026-09-22 review: codex_lane was a key nothing read; r2 (Sol): run only, prepare needs its seat
    assert run(e, "round", "close", "--feature", "09-22-x", "--kind", "d.sign")[0] == 2   # r2 (Sol): a free string reached the name pattern
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
    conf.write_text(conf.read_text(encoding="utf-8").replace('"astra"', '"opus"'), encoding="utf-8")
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
    (e.tmp / "gone.toml").write_text('[sol]\nmodel = "m"\neffort = "high"\ncommand = ["parsec-no-such-cli"]\n', encoding="utf-8")
    e.mp.setattr(parsec, "LANES_FILE", e.tmp / "gone.toml")
    code, out = run(e, "round", "run", "--feature", "panels/09-22-typo", "--kind", "panel", "--round", "1", "--lane", "sol", "--brief", str(e.brief))
    assert code == 64 and "not found on PATH" in out and not typo.exists()


# row 16: build run against a fake agy (2026-09-22 gemini_probes.py; 2026-09-12 and 09-13; old items 112 and 47a)
GOOD_LOG = "Print mode: starting with model gemini-3.8-flash-high\nPropagating selected model override\napplying agent mode accept-edits\nsilent auth succeeded\n"


def test_build_run_success_test(env):
    e = env
    run(e, "task-brief", "--feature", "09-22-x", "--task", "1")
    co = e.tmp / "checkout"
    git("worktree", "add", "--detach", str(co), e.head, cwd=e.repo)
    e.mp.setenv("FAKE_AGY_LOG", GOOD_LOG)
    e.mp.setenv("FAKE_STDOUT", "I made the edits.\n")
    e.mp.setenv("FAKE_ENV_DUMP", str(e.tmp / "env.json"))
    e.mp.setenv("FAKE_WRITE", str(co / "new.txt"))
    b = lambda *a: run(e, "build", "run", "--feature", "09-22-x", "--task", "1", "--checkout", str(co), "--head", e.head, *a)
    code, out = run(e, "build", "run", "--feature", "09-22-x", "--task", "1", "--checkout", str(co), "--head", "0" * 40)
    assert code == 64 and "not --head" in out                # 2026-09-22 17:23: the lane built on a tree the brief told it to refuse
    code, out = b()
    assert code == 0 and "result: ok" in out, out
    a = e.calls()[-1]
    prompt = a[a.index("-p") + 1]
    digest = parsec.sha256(e.feat / "build" / "task-01-brief.md")
    assert prompt.startswith(f"Read the file AGY-TASK-BRIEF-{digest[:12]}.md in the workspace") and prompt.endswith(parsec.CLOSING)
    assert a[a.index("--model") + 1] == "gemini-3.8-flash-high" and a[a.index("--mode") + 1] == "accept-edits"
    assert a[a.index("--add-dir") + 1] == str(co) and a[a.index("--log-file") + 1] == str((e.feat / "build" / "task-01-agy.log").resolve())
    child = json.loads((e.tmp / "env.json").read_text(encoding="utf-8"))
    assert child["AGY_CLI_DISABLE_AUTO_UPDATE"] == "true" and not list(co.glob("AGY-TASK-BRIEF-*"))
    report = (e.feat / "build" / "task-01-report.md").read_text(encoding="utf-8")
    assert report.startswith("I made the edits.") and "agy exit 0 (recorded, never trusted)" in report
    assert "build task 01 gemini: ok" in e.ledger()
    code, out = b("--again")
    assert code == 64 and "dirty before the build" in out      # 2026-09-22 review: a pre-dirty tree made the status test vacuous
    clean = lambda: (git("checkout", "--", ".", cwd=co), git("clean", "-fdq", cwd=co))
    clean()
    code, out = b()
    assert code == 64 and "--again archives it first" in out   # a report already present without --again (r2 Opus: was vacuous)
    e.mp.setenv("FAKE_AGY_LOG", GOOD_LOG + "soft-denying tool confirmation for RunCommand\n")
    code, out = b("--again")
    assert code == 65 and "FAILED: no soft-denied step" in out and (e.feat / "build" / "task-01-report.md.dead1").is_file()
    assert (e.feat / "build" / "task-01-agy.log.dead1").is_file() and not list(co.glob("AGY-TASK-BRIEF-*"))
    clean()
    e.mp.setenv("FAKE_AGY_LOG", GOOD_LOG)
    e.mp.setenv("FAKE_STDOUT", "")
    assert b("--again")[0] == 65                                # an empty final message despite exit 0
    clean()
    e.mp.setenv("FAKE_STDOUT", "done\n")
    e.mp.delenv("FAKE_WRITE")
    code, out = b("--again")
    assert code == 65 and "FAILED: git status non-empty" in out     # an empty diff is never done
    e.mp.setenv("FAKE_AGY_LOG", "Print mode: starting\n")
    e.mp.setenv("FAKE_WRITE", str(co / "new.txt"))
    code, out = b("--again")
    assert code == 65 and "FAILED: route line present: applying agent mode accept-edits" in out
    clean()
    (co / "crlf.txt").write_bytes(b"one\r\ntwo\r\n")
    git("add", "crlf.txt", cwd=co)
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "crlf", cwd=co)
    e.mp.setenv("FAKE_AGY_LOG", GOOD_LOG)
    e.mp.setenv("FAKE_WRITE", str(co / "crlf.txt"))                 # the fake writes LF into the CRLF file
    code, out = run(e, "build", "run", "--feature", "09-22-x", "--task", "1", "--checkout", str(co), "--head",
                    git("rev-parse", "HEAD", cwd=co).strip(), "--again")
    assert code == 65 and "FAILED: line endings kept" in out     # 2026-09-22 02:06: LF written into CRLF files, tests green
    clean()
    (co / ".gitignore").write_text(".claude/\nignored.txt\n", encoding="utf-8")   # a docs root git does not ignore, as setup allows
    conf = e.repo / ".claude" / "parsec.toml"
    conf.write_text(conf.read_text(encoding="utf-8").replace('docs_root = "docs"', f'docs_root = "{(e.repo / "docs").as_posix()}"'), encoding="utf-8")   # r3 (Sol): absolute too
    git("commit", "-qam", "docs tracked", cwd=co)
    (co / "docs" / "09-22-x" / "rounds").mkdir(parents=True)
    (co / "docs" / "09-22-x" / "rounds" / "pending.md").write_text("open round\n", encoding="utf-8")
    e.mp.setenv("FAKE_WRITE", str(co / "new.txt"))
    code, out = run(e, "build", "run", "--feature", "09-22-x", "--task", "1", "--checkout", str(co), "--head",
                    git("rev-parse", "HEAD", cwd=co).strip(), "--again")
    assert code == 0 and "result: ok" in out, out                # 2026-09-22 r2 (Sol): open rounds under a tracked docs root are not dirt
    clean()
    (co / "empty.txt").write_bytes(b"")
    (co / "lf.txt").write_bytes(b"one\ntwo\n")
    git("add", "empty.txt", "lf.txt", cwd=co)
    git("commit", "-qm", "empty and lf", cwd=co)
    b2 = lambda: run(e, "build", "run", "--feature", "09-22-x", "--task", "1", "--checkout", str(co), "--head", git("rev-parse", "HEAD", cwd=co), "--again")
    e.mp.setenv("FAKE_WRITE", str(co / "empty.txt"))              # w/none to w/lf: a first ending is no flip (r2, Sol)
    assert "ok: line endings kept" in b2()[1]
    clean()
    e.mp.setenv("FAKE_AGY_LOG", GOOD_LOG.replace("silent", "FAKE_CRLF silent"))
    e.mp.setenv("FAKE_WRITE", str(co / "lf.txt"))                 # the fake writes CRLF when its log says FAKE_CRLF
    assert "FAILED: line endings kept" in b2()[1]                  # LF to CRLF is a flip too (r2, Sol)
    clean()
    e.mp.setenv("FAKE_AGY_LOG", GOOD_LOG)
    e.mp.delenv("FAKE_WRITE")
    e.mp.setenv("FAKE_DELETE", str(co / "lf.txt"))
    assert "ok: line endings kept" in b2()[1]                      # r4 (Sol): a file the work tree lost has nothing to flip
    clean()
    real = parsec.git_out
    e.mp.setattr(parsec, "git_out", lambda a, c: (_ for _ in ()).throw(parsec.Exit(64, "ls-files failed")) if a[0] == "ls-files" else real(a, c))
    assert b2()[0] == 64                                           # r4 (Sol): a failed ls-files fails the build, never passes the check
    e.mp.setattr(parsec, "git_out", real)
    (e.repo / ".gitignore").write_text(".claude/\nignored.txt\n", encoding="utf-8")   # r4 (Opus): the primary itself, its docs root tracked
    git("add", ".gitignore", "docs", cwd=e.repo)
    git("commit", "-qm", "docs tracked", cwd=e.repo)
    (e.feat / "ledger.md").write_text(e.ledger() + "- a line\n", encoding="utf-8")
    e.mp.setenv("FAKE_WRITE", str(e.repo / "new.txt"))
    code, out = run(e, "build", "run", "--feature", "09-22-x", "--task", "1", "--checkout", str(e.repo), "--head", git("rev-parse", "HEAD", cwd=e.repo), "--again")
    assert code == 0 and "result: ok" in out, out                  # the feature's own ledger and spec are not dirt either
    code, out = run(e, "build", "archive", "--feature", "09-22-x", "--task", "1")
    assert code == 0 and ".dead11" in out and not (e.feat / "build" / "task-01-report.md").exists()


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
