# Kimi CLI

Version in use when written: kimi-code 0.43.1 (2026-09-21).

- **The lane home.** The lane runs with `KIMI_CODE_HOME` set to the folder named in `lanes.toml` (`home`), because the normal home's login was dead on 2026-09-21. The lane home's `config.toml` carries the model alias `kimi-code/k3` and its `default_effort`; the pre-flight checks both are present. The `credentials` folder is never opened; diagnostics print presence only.
- **`--plan` refuses `-p`** (`Cannot combine --prompt with --plan`, 2026-09-21), so a round never passes `--plan`.
- **The token lives 900 s** with a rotating refresh token and no lock file. Two rounds at once across two refreshes were measured safe on 2026-09-21 (`kimi_two_at_once.py`: 666 s and 1,113 s, two quick rounds started on an expired token, all exit 0, the credentials file rewritten once per expiry). Not covered: three or more at once, other versions.
- **The session id is printed only at the end** (2026-09-21), on standard error, as `To resume this session: kimi -r session_<uuid>`; the tool passes that token to `--session` as printed. Whether `--session` also takes the bare uuid is unmeasured.
- **The reply is standard output** (2026-09-21), UTF-8; thinking goes to standard error as the round runs, which is how the watcher sees life.
