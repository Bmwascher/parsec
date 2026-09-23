# Changelog

Newest first. Each section opens with plain words for the user; the detail follows.

## v0.1.12 (2026-09-23)

The Gemini build lane works again with a relative checkout path. Each round now prints the first lines of its summary.

- `build run` gives agy the full path of the checkout. With `--checkout .` agy did not find the workspace and did not read the files.
- `round run` and `round collect` print the title line and the counts line of the round summary. Each brief asks the reviewer for one counts line.
- The debate skill says that a reference outside the reference folder goes in as a `--file` evidence file. Item 10 of the list is closed.
- The skills and templates are shorter: a rule keeps the date of its failure, and the full account stays in the notes.

## v0.1.11 (2026-09-23)

The spec and the task list are shorter to review and easier to build. The tool now records the second question to Opus or Fable as a resume of the same agent.

- Each spec opens with a decision summary of 150 words or less. The driver posts it in chat. Brandon reviews the spec before the task list, also when the handoff gives the go.
- The task list uses one edit format: a quoted anchor line, then the new text. Each task has a list of checks and its own commit.
- The author rewrites each section that a review result changes. Then the author checks the summary, the goal and the behaviour again.
- The ledger template gives one shape for each decision, waiver, owed look, gate result and smoke test. A hand-written line has 200 characters or less. The tool refuses a reason that has more than 130 characters.
- The setup skill is the one home of the feature folder. All the files of a feature stay in that folder.
- `round collect --agent-id` records the agent of an Opus or Fable round. `round prepare --resume` records the next round as a resume of that agent and checks the ID against the last record. Without it, an Opus or Fable round starts fresh.
- The model notes are shorter by 314 words. The Fable note names the design look.
- The readme and the project rules now say that the final PASS can also name the commit of a "fix now" Minor.

## v0.1.10 (2026-09-23)

Each review brief now tells the reviewer what is final, what changed and what to check. Fable also reviews the plan before the build.

- The context file of each round starts with the read and run rules of its lane. Sol and Astra can read with shell commands. Kimi, Opus and Fable use their file tools only.
- A diff gate round of a feature with a design gets the spec, the task list and the list of amendments.
- The brief template has a record part. It lists the settled points, the accepted residuals and the answer to each result of the last round. Each claim has a number.
- The new last-look insert serves the two Fable looks. In the last look, Fable sorts each open Minor result into "fix now" or "ride".
- The debate skill adds the Fable design look after the design debate. The session closes a round on Minor results only when the reviewer gave each open result the grade Minor.
- The driver rules let a command that ends in less than a minute run in the foreground with a timeout.
- A diff, pre-review or last-look round makes no panel folder. The "already collected" message names `round run` only for a CLI lane.

## v0.1.9 (2026-09-23)

Opus and Fable review the correct commit. The doctor and the pre-flight are easy to read on a phone.

- `round prepare` makes a review worktree at `--head` for Opus and Fable, as `round run` does for the other lanes. `round close` removes it.
- The tool changes `--base` and `--head` to full commit IDs before it starts a round.
- A last look on a lane other than Fable is a degraded stand-in. A Fable last look on the same head replaces it.
- The doctor compares the installed copy with the source repository, not with the cache. It shows a colour on the install line and on each lane line.
- Each command warns you when you have a newer parsec than the one that runs.
- The pre-flight shows a colour, the feature and one bullet for each check. It also checks `--feature`.
- `--feature` can start with the docs root.
- `round prepare` shows the path to the brief. The context file gives the name of each evidence file.
- The tool budget is 1,250 lines. The prose budget is 11,000 words.

## v0.1.8 (2026-09-23)

Round summaries are easy to read on a phone. A mistyped panel name makes no folder.

- The debate skill gives a new shape for the round summary. The title shows a colour and the verdict. One line shows what needs Brandon. Each result of the review has one bullet with its answer. Do not put the summary in a code block.
- The five-round limit counts the rounds of one lane and one kind.
- Only `round prepare` and `round run` make a panel folder, and only for round 1. They make the folder after all of their checks.
- `round prepare` and `round run` check the evidence files, the commits and the design files before they write anything. They refuse an evidence file in the round folder that a rerun moves. `round run` also finds the CLI before it writes anything.
- If you did not collect a round, the tool tells you to collect it. It does not tell you the next round number.
- The prose budget is 10,200 words.

## v0.1.7 (2026-09-22)

Each lane now counts its own rounds of a kind from 1. A first diff round is round 1, not the next number of the feature.

- `round run` and `round prepare` refuse a round number that is not the next one for that lane and kind, and name the correct number.
- A round with no verdict runs again under the same number.

## v0.1.6 (2026-09-22)

The Gemini lane is now the implementer, and the Opus agent is the backup implementer.

- The agent `implementer` is now `backup-implementer`. The build skill sends it the same tasks as before.
- The skills, model notes, templates and README use the new names.

## v0.1.5 (2026-09-22)

The design skill is now the brainstorm skill. Say "brainstorm" to start a feature.

- The skill folder, its name and every reference to it use `brainstorm`.
- The review kind `design` keeps its name, so round folders and commands do not change.

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
