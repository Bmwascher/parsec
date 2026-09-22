"""The fake CLI every parsec test runs instead of codex, kimi or agy: records what it was given and
replies as told through FAKE_* variables. One JSON array of arguments per call in FAKE_LOG."""
import json, os, subprocess, sys, time
from pathlib import Path

argv = sys.argv[1:]
env = os.environ
with open(env["FAKE_LOG"], "a", encoding="utf-8") as f:
    f.write(json.dumps(argv) + "\n")
if env.get("FAKE_ENV_DUMP"):
    Path(env["FAKE_ENV_DUMP"]).write_text(json.dumps(dict(env)), encoding="utf-8")
if argv[:1] == ["--version"]:
    print(env.get("FAKE_VERSION", "fake-cli 1.0")); sys.exit(0)
if argv[:2] == ["login", "status"]:
    print(env.get("FAKE_LOGIN", "Logged in using ChatGPT")); sys.exit(0)
if env.get("FAKE_STDIN_COPY"):
    Path(env["FAKE_STDIN_COPY"]).write_bytes(sys.stdin.buffer.read())
if env.get("FAKE_CHILD_PID_FILE"):                       # a grandchild that must die with the fake
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(600)"])
    Path(env["FAKE_CHILD_PID_FILE"]).write_text(str(child.pid))
if env.get("FAKE_WRITE"):                                # a reviewer that writes into the tree
    Path(env["FAKE_WRITE"]).write_bytes(b"written by the reviewer\r\n" if "FAKE_CRLF" in env.get("FAKE_AGY_LOG", "") else b"written by the reviewer\n")   # bytes: write_text made CRLF on Windows (2026-09-22 review)
if "--log-file" in argv:                                 # agy: the log the success test reads
    Path(argv[argv.index("--log-file") + 1]).write_text(env.get("FAKE_AGY_LOG", ""), encoding="utf-8")
time.sleep(float(env.get("FAKE_SLEEP", "0")))
sys.stdout.write(env.get("FAKE_STDOUT", ""))
sys.stderr.write(env.get("FAKE_STDERR", ""))
if "--output-last-message" in argv and env.get("FAKE_REPLY") is not None:
    Path(argv[argv.index("--output-last-message") + 1]).write_text(env["FAKE_REPLY"], encoding="utf-8")
sys.exit(int(env.get("FAKE_EXIT", "0")))
