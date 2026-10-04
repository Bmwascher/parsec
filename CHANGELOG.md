# Changelog

Newest first. Each section opens with plain words for the user; the detail follows.

## v0.1.24 (2026-10-04)

A task that changes only files in the docs root no longer shows as failed when its Files line has no list mark.

- `build run` found the files of a task only on a line that starts with `- **Files**:`. Authors also write `**Files**:`, `- **Files:**` and `**Files:**`. With such a line the task named no file. Then a task that changed only a file in the docs root failed the success test, although the edit was correct.
- This occurred in task 2 of the KitnEssentials phase ap-2. The junction of `dev/docs` in the worktree was not the cause.
- Now `build run` reads all four forms. The tool can only find more files than before, so a task that passed still passes.

## v0.1.23 (2026-10-04)

A task now gets its full brief when it shows a Markdown title line in a code block.

- `task-brief` stopped a task at a line that starts with `## ` in a fenced code block. Examples are a line of a `.toc` file and a line of a smoke file. The implementer then got only a part of the task. This occurred in eight briefs of KitnEssentials. Now the tool ignores the lines in a fenced code block when it finds the sections.
- The same rule applies to three more parts of the tool. They are the Files field of `build run`, the rubric sections of the pre-flight and the insert point of a review brief.
- The task list template tells the author to put a longer fence around a fence. An indent of three spaces or less does not keep a fence open.

## v0.1.22 (2026-09-30)

The Sol lane now uses GPT-6.1 Sol. This is the default reviewer from other companies.

- The Sol lane runs `gpt-6.1-sol` at high effort. Before, it ran `gpt-6-sol`. The id works on codex-cli 0.159.2.
- OpenAI has no guide for prompts to GPT-6.1 Sol yet. The model note records this. It also records the results of the first test and the default effort values.
- The measurements of GPT-6 Sol stay in the note, marked as not yet measured on GPT-6.1.

## v0.1.21 (2026-09-28)

The rules now protect the words and decisions of Brandon when another session acts for him. The rules come from the audit of the Groundhog Key programme.

- A delegator quotes the words of Brandon as he typed them and marks its own words. It decides only what his words give it, and only for the phase that he names. The ledger and the finish report show each such decision as the decision of the delegator.
- Brandon can let a delegator approve a spec. His go-ahead words can also skip his own read of the spec. Neither choice skips the design debate or the Fable design look. If Brandon did not approve the spec himself, the finish report includes its decision summary.
- A fix in the diff gate that changes what the feature does waits for the answer of Brandon.
- Each review result that goes to the author asks for a fix at every site of its class. A fix by the session in bounded work does the same.
- The finish report lists each open item that Brandon did not decide, each site that stays open and each delegated decision.
- The ledger has shapes for relayed words, delegated decisions, a Minor fix by the session and a skipped read of the spec. The head is the one place for the base.
- After a compaction, the session reads the rules, the skill and the ledger again.
- The model notes use the numbers from the audit.
- `round prepare` gives no warning for a bare file name when the code has a file of that name in a subfolder.
- The prose limit is now 12,000 words, on the word of Brandon. The prose is 11,205 words.

## v0.1.20 (2026-09-28)

The prose is 79 words shorter, at 10,904 of 11,000. This gives room for the next batch of rules.

- Twelve cuts remove text that another file already holds, old history and extra words. Each cut keeps its rule, condition and dated measurement.
- A Fable poll checked each cut before the edit. It kept one reason that makes a rule clear, and it corrected one note.

## v0.1.19 (2026-09-28)

The tool takes the fixes from the third field audit, of the 16 phases of the Groundhog Key programme.

- The tool also adds each round summary to `summaries.md` in the feature folder. The finish report includes this file, so Brandon can read every round in a phase that a delegator runs. In the field, 68 of 153 summaries went to the chat, and no delegator got one.
- The summary bullets keep the backticks in a title. A long title stops at a word and closes an open code span. When a Fable look counts findings from other lanes, the tool keeps the bullets that it can read. A `?` bullet shows each of the others. The answer slot has no angle brackets, because Monitor changed them to `&lt;` and `&gt;`.
- The package holds `notes.md`. `round prepare` and `round run` give a warning when the brief names a file that the package and the code do not hold. They also give a warning when a gate round gets no evidence file other than replies. In the field, reviewers could not find `notes.md` in three phases, and gate logs went in as evidence in 4 of 16 phases.
- The tool adds the CONTINUITY question to each resumed round. Before, a brief made from an earlier brief lost the question in one phase.
- The lane line says that `rg` is not on the path of the sandbox. Sol read the old words as a fact about the project four times.
- Each record keeps a hash of the reply. `round collect` gives a warning when an earlier reply changed after its collect. In one phase, the author wrote over the reply of Sol.
- The success test of `build run` accepts a change to a docs-root file that the Files field of the task names. In the field, a task that changed only the smoke file failed the test.
- The prose is 6 words shorter, at 10,983 of 11,000.

## v0.1.18 (2026-09-28)

The prompt for the Gemini lane tells Gemini to find text with its own search tool.

- The last sentence of each agy prompt now names the `grep_search` tool of agy as the way to find text, and not a command. In the field, 4 of 232 build runs stopped because Gemini tried a `Select-String` search as a command, which print mode does not permit. The backup implementer then built each of these tasks.
- In three probe runs with the new prompt, Gemini made each edit and tried no command. It read the file with `ViewFile` and did not use `grep_search`. No field run has measured the effect of the prompt yet.
- The prose is 21 words longer, at 10,989 of 11,000.

## v0.1.17 (2026-09-28)

The Gemini lane can read and edit the files of a feature in the primary checkout when it builds in a worktree.

- `build run` gives agy the docs root as a second workspace folder when the docs root is not in the checkout. Before this change, agy did not let Gemini read a spec or a local smoke file by its path in the primary checkout. The task then stopped with no edits, and the backup implementer built it (KitnEssentials, 2026-09-27).
- An edit in the docs root, such as a step in the smoke file, is not in a git diff. The build skill tells the session to open the file.
- The agy note gives the refused reads, the probes on agy 1.2.10 and one more try of `RunCommand`.
- The prose is 133 words longer, at 10,968 of 11,000.

## v0.1.16 (2026-09-26)

The skills, templates and model notes take the rules from the second field audit. The tool sorts the round summary by grade.

- The driver gives each problem to the author with its evidence and names no fix. A code fix by the author covers each place of the same pattern, or names the places that stay open for Brandon.
- The decisions of Brandon stay with him. No project rule or handoff takes one for him, and a delegator sends each "Needs you" and each spec review to him. A brief lists a residual without his words as open.
- The decision summary of a spec names each follow-up that the design makes. After approval, the author writes the approved decisions into the summary.
- The driver sends a plugin agent with no `model` value, so the agent uses the model that its file names.
- A hand ledger line takes its time from `date` or `Get-Date` in the same command. The ledger template has a shape for a spec approval and a shape for a ride on the triage of a reviewer.
- Before each new dispatch of a build task, the session puts the writes of the failed try in a stash. A difference of whitespace only does not go to a second dispatch. The session removes it and notes it in the ledger line of the task.
- The model notes give the numbers from the field. The agy note names `silent auth succeeded` as the login line.
- The round summary shows the Critical problems first, then Important, then Minor.
- The prose is 95 words longer, at 10,835 of 11,000.

## v0.1.15 (2026-09-25)

The tool now adds the insert to each brief and prints the full round summary. These changes come from the second field audit.

- `round prepare` and `round run` add the insert for the kind of round at the end of part 2 of the brief. The driver writes only the shared text. A resumed question to the same agent and a brief with no part 3 get no insert. The tool refuses a brief that already has an insert.
- The tool prints the round summary with one bullet for each problem that the reviewer found. When these lines of the reply do not agree with its counts line, each bullet shows `?`, and the tool gives a warning. The tool also gives a warning when a reply has no counts line.
- The `VERDICT:` line must be the last line of the reply. Before this change, a reply with text after its verdict line gave a verdict. When the last line is not a verdict line, the tool gives a warning to run the round again on the same session.
- The warning for an old tool version says that the skills stay old until a new session starts. It gives the path of the new tool.
- For a round with no reply, the ledger line says `no reply`.
- The page size for `diff.patch` agrees with the limit of the Read tool.
- `verify --record-amendment` stops while a round has a package but no record.
- The brief template asks for one line for each problem and names `.parsec/context.md`.

## v0.1.14 (2026-09-24)

The Kimi lane works on Kimi CLI 2.1.1. The tool now reads a Kimi verdict that starts a reply block.

- Kimi starts each reply block with a bullet. The tool removes the bullet before it reads a `VERDICT:` or `CONTINUITY:` line. Before this change, such a line read NONE.
- `doctor --update` runs `kimi update -y`. Without `-y`, Kimi asks for a yes, and the doctor cannot answer.
- The Kimi CLI note gives the measurements on 2.1.1. The weekly Kimi quota stopped one case of two rounds at once, so that case has no measurement on 2.1.1.

## v0.1.13 (2026-09-23)

The skills, templates and model notes are shorter by about 260 words. No rule changed.

- A rule that two files stated now lives in one file, and the other file points to it when its reader needs the pointer.
- The model notes lose old history and stale lines.
- The debate skill now says that for bounded work the session makes the feature folder and writes the ledger head before the first diff round.

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
