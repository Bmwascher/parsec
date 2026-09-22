# agy (the Antigravity CLI): the build lane's CLI

Runs Gemini 3.8 Flash (`gemini-3.8-flash-high`) in print mode for `build run`. Version in use when written: 1.2.5 (2026-09-22). The guards themselves (the route lines, the success test, the updater variable) live in the tool; this file holds the dated facts behind them.

- **The trust list is not an authorization control** (old item 105, 2026-09-17): nothing mechanical refuses an `--add-dir` outside it. The checkout is the child's working folder and its `--add-dir`.
- **The updater** (old item 112, measured 2026-09-17 on 1.2.4): the throttled auto-updater opened a console that took the foreground; `AGY_CLI_DISABLE_AUTO_UPDATE=true`, the literal `true`, disables it (at `1` it still ran). A deliberate update is `agy update` ("Update CLI", checked 2026-09-22), run by `doctor --update`.
- **Print mode runs no command and has no delete tool** (2026-09-22, `gemini_probes.py`): a `RunCommand` was soft-denied; a task that deletes, renames or moves a file goes to the `implementer`.
- **A soft-denied step ends the run with exit 0 and an empty reply** (two probes, 2026-09-22). So the exit code is recorded and never trusted, and an empty final message fails the success test.
- **It never reports blocked** (2026-09-22): on a checkout one commit too early it read two errors on the missing dependency, edited on, and reported success. The failed test run is the signal; the diagnosis order is in `build`.
- **New-file writes work** (`WriteToFile`, 2026-09-22); a first probe wandered to the workspace's parent when the workspace was nested under the working folder.
- **Gemini's tokens are recorded nowhere** the tool can read; a task's cost on this lane is time only (63 s on Task 2 of the 2026-09-22 comparison, 0 Claude tokens).
- **`--mode accept-edits`**: without it the edit was soft-denied (1.2.0, 2026-09-12).
- **Auth is a silent refresh** (2026-09-22) seen only in the log (`silent auth succeeded`, or `not authenticated`); the first run's log is the login check.
