# Changelog

Newest first. Each section opens with plain words for the user; the detail follows.

## v0.1.4 (2026-09-22)

The fourth round's findings. A build in the main checkout works when git tracks the docs root.

- The build's status and line endings checks skip a docs root inside the checkout, absolute or relative, never the whole checkout.
- `round run` checks the config's lane before it makes a panel folder.
- Tests for a deleted file, a failed `ls-files`, the quota reader's early return and a build in the main checkout.

## v0.1.3 (2026-09-22)

The findings of the second and third rounds, fixed the same evening.

- `round run` refuses a config `codex_lane` that is not a lane before it writes anything.
- The build's status checks exclude only the round, build and panel folders under the docs root, absolute or relative.
- A file that the work tree lost does not count as a flip; a failed `ls-files` now fails the check.
- The quota probe stops at the first answer and ends its process tree; the doctor names every lane an update serves.
- The pre-flight's rubric line counts rubric files, not sections. Tests for each, and for the record before the ledger line.
- A round that lost its review tree collects as NONE; `round prepare` needs its seat.
- `round close --kind` takes only the known kinds; a file with no line break yet is no flip.

## v0.1.2 (2026-09-22)

Fifteen reviews of the plugin found these the same day. The tool now reads the config's codex lane, the doctor fails without a config, and the build guards hold under every git setting.

### Tool

- `round run` takes the config's `codex_lane` without `--lane`, `round prepare` still names its seat; the setup skill named the key and nothing read it.
- The line endings check compares the work tree before and after the build, so it holds under `autocrlf` and on renamed or quoted paths.
- `build run` refuses a dirty checkout and an empty `--head`, and a capped run names its reason.
- The doctor exits 64 without a config, prints a login line for every lane and runs one update per CLI. A rubric file that does not exist fails the pre-flight.
- `--feature` cannot leave the docs root; `round close` matches whole worktree names; the round's record outlives the ledger line.
- The quota read has a deadline and always ends its child; an unknown `doctor --lane` exits 64; an Opus last look carries the Opus name.

### Prose

- The author, never the session, writes and answers; skill command examples carry every necessary argument; brief rules have one home.
- Every cited model-note line carries its date.

## v0.1.1 (2026-09-22)

The seats and lanes settled by the day's measurements, and six guards, each named after a failure seen that day.

### Seats and lanes

- Opus 5.5 holds the author, pre-review and implementer seats; the session always dispatches the author.
- GPT-6 Sol is the default codex lane, Astra the alternate by name. A new id refused on an old CLI wants the update, not an entitlement.

### Guards

- `build run` takes `--head` and refuses a checkout at any other commit; the lane never checks.
- After a build, a modified file whose line endings flipped fails the task.
- A panel round no longer needs `--head`; it takes the primary's HEAD.
- The author never reopens a question the notes answer, and quotes an anchor as a whole line.
- The doctor's STALE line says what to do: bump the version, then update the plugin.
- `.gitattributes` keeps every text file LF on checkout.

## v0.1.0 (2026-09-22)

First scaffold of the plugin that replaces superpowers and the old parallax plugin. Five skills, one Python tool, eight files carried from the old repo, and tests that each stand on a recorded failure.

### Skills

- `design`, `build`, `debate`, `setup` and `panel`, each with one home per rule.
- Templates for the spec, the task list, the brief and its three inserts, the ledger, the driver rules and the implementer contract.

### Tool

- `tools/parsec.py` runs a review round on a codex or Kimi lane and prepares the package for an Opus or Fable lane.
- The same tool collects the record, checks the two design files against the newest record, and slices a task brief.
- It also runs the Gemini build lane, removes a review worktree, and prints the doctor table.

### Carried from the old repo

- The STE checker, the changelog checker, their tests, the Kimi agent file, the licence and the release workflow.
