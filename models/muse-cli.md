# Muse Code CLI

Version in use: Muse Code 1.4.6 (1.4.6-R6000.1), 2026-10-12. Docs: https://dev.meta.ai/docs/muse-code, fetched 2026-10-12.

- **Login.** `muse login` signs in through the browser and has no status command, so the pre-flight and the doctor check only that `~/.config/muse/auth.json` exists; the file is never opened.
- **Updates.** On each start the launcher checks for an update after an interval and installs it in a hidden background process. 1.4.6 has no update subcommand; `doctor --update` updates Muse in the foreground.
- **Exit codes** (the docs' "Extending and automating"): 0 completed; 1 failed or cancelled, the step cap included; 2 a usage error; 130 or 143 a signal.
- **The reply arrives at exit.** In a 300 s round, `reply.md` stayed empty until the end and standard error stopped after the start, while the session's `session.jsonl` grew every 15 to 45 s: the "last write" age comes from it.
- **Expected warnings** on standard error, none a failure: a rules file skipped because the workspace is untrusted, agent delegation unavailable, a Claude plugin file seen as diagnostics only.
- **Quota.** A round costs more quota than the same prompt in Brandon's own sessions, where contributor mode is on and buys more usage (Q2-A).
- **Measured 2026-10-12.** Two pairs of rounds at once: all exit 0 and PASS; one pair took 26 to 33 s, the other 173 to 249 s, cause unmeasured. A 2,119-line package: PASS in 97 s.

## Unmeasured

- What a spent quota prints, and its exit code.
