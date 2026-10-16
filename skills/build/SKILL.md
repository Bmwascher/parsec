---
name: build
description: Use when a designed feature has a go on record and is to be built, or when bounded work has Brandon's yes. Builds each task of the task list through the Gemini lane (or the `backup-implementer` where Gemini cannot), checks and commits each task in the session, then runs the diff gate and finishes as the project's rule says.
---

# build

Rules that cut across the flow are in `${CLAUDE_PLUGIN_ROOT}/templates/driver-rules.md`; read it first. The tool is `${CLAUDE_PLUGIN_ROOT}/tools/parsec.py`, run with `python`; its `--help` carries the argument detail.

## Start

- Refuse to start without a recorded go (`brainstorm`), or without a design look after the last cross-vendor design round: a `design r<n> fable` ledger line, or, on Brandon's `waiver` ledger line for the stand-in, an Opus stand-in's `design r<n> opus` line (`debate`, "The Fable looks").
- Run `verify --feature <folder>`: MATCH and MATCH (CLOSED ON MINOR) continue; MATCH (DEGRADED PASS) and CHANGED stop and ask Brandon; NO-PASS-YET refuses.
- Read the base from the ledger head (written once, by `brainstorm`). A fresh worktree lacks the project's gitignored hook inputs (KitnEssentials: `dev\githooks\upstream-names.local.sh`); copy them before the first commit (2026-09-22). Work in the checkout the session was handed, or make one at `<worktrees>\<Project>-<branch>` and record in the ledger that `build` made it. Only a worktree `build` made is ever removed by it, and never under stop and report.

## Bounded work

Skips all of the above: no `verify`, Brandon's yes is the go, the session builds and commits it, then runs the diff gate (`debate`, `--kind diff`). A BLOCKING code finding there is fixed by the session directly (no task list, no `author`, no `verify`), and the next round runs on the new head. A session fix covers every site or input order of its class, or names those left open (2026-09-28).

Its class is checked out loud first (`brainstorm`), and a claim it rests on is probed first (driver rule 7).

**A small change** passes the gate with no cross-vendor round when a reader can judge it right from the diff alone (values, labels, renames, a new entry in an existing table, a copy of a pattern already in the same file); it has 20 or fewer changed lines (`git diff --numstat`, added plus removed) in 2 or fewer files, test files counted in the lines but not the files; it adds or changes no game API call, hook, event handler or timing; and no Opus pre-review round on it found a Critical or Important. After that PASS the driver checks each point and writes the `small` ledger line; a delegator never makes this call for a phase chat. The Fable last look still runs, and its posted summary and the finish report say `small: no cross-vendor round` (Brandon, 2026-10-15).

## Each task, in order

1. **Before task 1**: `doctor --lane gemini --kind build --feature <folder>` in the background (`Pre-flight: Gemini`), posted as is. When it finds no agy, every task goes to the `backup-implementer`.
2. `task-brief --feature <folder> --task N` writes `build\task-NN-brief.md` (the task, the header and the global constraints, byte for byte) and prints its SHA-256.
3. `build run --feature <folder> --task N --checkout <path> --head <commit>` in the background, named `Task N Implement`, where `--head` is the commit the task builds on (the ledger base, then the previous task's commit). The tool refuses any other checkout, refuses a dirty checkout and fails a task that flipped a modified file's line endings; the lane checks none of these (2026-09-22). The tool runs agy, writes `build\task-NN-report.md` and prints the success test. The session reads that, never agy's exit code.
4. **The session checks the task itself before the next**: run the task's **Checks** in the background (a Gemini task's first run, since print mode runs no command). On the Gemini lane a task with a test is first run red: stash the task's non-test files by name (`git stash push --include-untracked -m "<feature> task N red" -- <files>`), run the Checks and see the expected failure, pop that entry by its `stash@{k}` in `git stash list`, never a bare pop (field audit 4: one reached a leftover stash), then run them green. With no entry of that name, nothing is popped and no red is recorded; Checks still green with the files stashed mean the test proves nothing ("A failing task", step 3). Then read the diff against the task's files and its fenced code (an edit in the docs root, such as the smoke file, is in no diff: open the file); then make the task's commit with the task's own commit step. No per-task reviewer subagent.
5. Ledger line: the task's commit and result, with the lane that built it.

## To the `backup-implementer` instead

Dispatch `agents/backup-implementer.md` in the background, named `Task N Implement`, with the brief path, the contract path (`templates/implementer-contract.md`), the checkout and a report path, for:

- a task that deletes, renames or moves a file (print mode has no delete tool);
- a task that copies or writes a binary file, such as an image (print mode runs no command; KitnEssentials ap-15 task 1, 2026-10-05);
- a task whose Gemini run failed the success test once, or whose diff did not match its code (below);
- every task when the pre-flight finds no agy.

Run `build archive --feature <folder> --task N` before ANY redispatch of a task that already has a report, so no attempt's evidence is overwritten. Before ANY redispatch, stash the attempt's writes (`git stash push --include-untracked -m "<feature> task N attempt k" -- <its files>`, 2026-09-24). The `backup-implementer` reports blocked itself.

## A failing task

A task whose CODE is wrong is the author's defect. Gemini never reports blocked (2026-09-22), so on that lane the failed test run is the signal, and the session names the cause in this order (agy's log: `models/agy-cli.md`):

1. **The diff does not match the task's code**: a transcription failure. The task goes to the `backup-implementer` as its second dispatch. A whitespace-only mismatch is not: the session trims it and notes it in the task's ledger line (2026-09-23).
2. **The diff matches**: check the base first. The checkout must sit at the previous task's commit and every file the task consumes must exist (2026-09-22: a run on a checkout one commit early). A wrong base is the session's to fix before it dispatches the task again; that redispatch still counts.
3. **The base is right**: the task is wrong. The `author`, resumed, amends it; `verify --feature <folder> --record-amendment "<reason>"` records it; the gate's `context.md` lists it. No extra round unless the amendment changes something another task consumes; then Brandon is asked.

A second failed dispatch of the same task, for ANY reason, amendment cycles included, goes to Brandon.

## After a compaction

A `task-NN-brief.md` with no `task-NN-report.md` beside it means a build may still be running, on either lane. Check the background task list before dispatching that task again (undated).

## The gate and the finish

Then the diff gate (`debate`, `--kind diff`), then the finish. The gate runs first, the project's human check (a smoke, on Brandon's yes) last, on the final head. A commit other than a gate fix or the release's version bump, which the last look reviews, added after the pre-review was packaged, restarts the gate on the new head. A fix for a symptom seen in game passes `--reference` when its module was ported (`debate`), and its gate summary says the PASS covers the code, not the symptom: the smoke decides.

The finish is STOP AND REPORT unless Brandon, a handoff or the project's finishing rule says merge or pull request. The report takes the shape and destination the handoff or project gives, and lists every open Minor finding, every refutation the driver made and every round it closed on Minor findings, each with its reply path, then every "Open, not ruled" item, every site left open for Brandon and every delegated decision, for him to confirm or reverse, so nothing decided on Brandon's behalf is silently dropped, and carries `summaries.md` whole and, unless he approved the spec himself, the decision summary, which a delegator's relay keeps (2026-09-28). A degraded gate blocks a clean report. Only the commit the final PASS names is merged.

A rebased head counts as the commit the final PASS names only when `git patch-id --stable` gives the same id for the passed range and the rebased one, and the project's checks are green on it; otherwise the last look runs again on it. When the feature merges, the session drops each stash it made for it, by its `stash@{k}` in `git stash list`, where the project's guard allows; the finish report lists each stash it did not drop by its message, with the one command for Brandon. A worktree the session made by hand for a review or a check, not the checkout `build` made (Start), is removed when its step ends.

## Ledger lines this skill writes

Step 5's task line, the worktree line (Start), the small line (Bounded work), each probe result or claim waiver (driver rule 7, Bounded work), each gate result, the smoke, the finish.
