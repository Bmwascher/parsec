# agy (the Antigravity CLI): the implementer lane's CLI

Runs Gemini 3.8 Flash (`gemini-3.8-flash-high`) in print mode for `build run`. Version in use when written: 1.2.5 (2026-09-22). The guards themselves (the route lines, the success test, the updater variable) live in the tool; this file holds the dated facts behind them.

- **The trust list is not an authorization control** (old item 105, 2026-09-17): nothing mechanical refuses an `--add-dir` outside it. The checkout is the child's working folder and its `--add-dir`.
- **The updater** (old item 112, measured 2026-09-17 on 1.2.4): the throttled auto-updater opened a console that took the foreground; `AGY_CLI_DISABLE_AUTO_UPDATE=true`, the literal `true`, disables it (at `1` it still ran). A deliberate update is `agy update` ("Update CLI", checked 2026-09-22), run by `doctor --update`.
- **Print mode runs no command and has no delete tool** (2026-09-22, `gemini_probes.py`): a `RunCommand` was soft-denied.
- **A soft-denied step ends the run with exit 0 and an empty reply** (two probes, 2026-09-22).
- **It never reports blocked** (2026-09-22): on a checkout one commit too early it read two errors on the missing dependency, edited on and reported success. The diagnosis order is in `build`.
- **`--add-dir` needs an absolute path** (field phase 5b, 2026-09-23): given `.`, agy logged `failed to resolve --add-dir path "."`, dropped the workspace and soft-denied its reads.
- **New-file writes work** (`WriteToFile`, 2026-09-22); a first probe wandered to the workspace's parent when the workspace was nested under the working folder.
- **Gemini's tokens are recorded nowhere** the tool can read; a task's cost on this lane is time only (63 s on Task 2 of the 2026-09-22 comparison).
- **`--mode accept-edits`**: without it the edit was soft-denied (1.2.0, 2026-09-12).
- **Auth is a silent refresh** (2026-09-22) seen only in the log's `silent auth succeeded` line; the `not logged into Antigravity` lines are in every log (2026-09-24); the first run's log is the login check.
- **In the field** (2026-09-23 to 25): print mode stops at 5 minutes; it tried `RunCommand` twice, on the widest tasks; it miscopied a value yet reported success; it adds stray blank lines.
