---
name: build
description: Use when a designed feature has a go on record and is to be built, or when bounded work has Brandon's yes. Builds each task of the task list through the Gemini lane (or the `backup-implementer` where Gemini cannot), checks and commits each task in the session, then runs the diff gate and finishes as the project's rule says.
---

# build

Rules that cut across the flow are in `${CLAUDE_PLUGIN_ROOT}/templates/driver-rules.md`; read it first. The tool is `${CLAUDE_PLUGIN_ROOT}/tools/parsec.py`, run with `python`; its `--help` carries the argument detail.

## Start

- Refuse to start without a recorded go (`brainstorm`), or without a design look after the last cross-vendor design round: a `design r<n> fable` ledger line, or on Brandon's recorded word an Opus stand-in's `design r<n> opus` line or none (`debate`, "The Fable looks").
- Run `verify --feature <folder>`: MATCH and MATCH (CLOSED ON MINOR) continue; MATCH (DEGRADED PASS) and CHANGED stop and ask Brandon; NO-PASS-YET refuses.
- Read the base from the ledger head (written once, by `brainstorm`). A fresh worktree lacks the project's gitignored hook inputs (KitnEssentials: `dev\githooks\upstream-names.local.sh`); copy them before the first commit (2026-09-22). Work in the checkout the session was handed, or make one at `<worktrees>\<Project>-<branch>` and record in the ledger that `build` made it. Only a worktree `build` made is ever removed by it, and never under stop and report.

## Bounded work

Skips all of the above: no `verify`, Brandon's yes is the go, the session builds and commits it, then runs the diff gate (`debate`, `--kind diff`), whose ledger head records the base. A BLOCKING code finding there is fixed by the session directly (no task list, no `author`, no `verify`), and the next round runs on the new head.

## Each task, in order

1. **Before task 1**: `doctor --lane gemini --kind build --feature <folder>` in the background (`Pre-flight: Gemini`), posted as is. When it finds no agy, every task goes to the `backup-implementer`.
2. `task-brief --feature <folder> --task N` writes `build\task-NN-brief.md` (the task, the header and the global constraints, byte for byte) and prints its SHA-256.
3. `build run --feature <folder> --task N --checkout <path> --head <commit>` in the background, named `Task N Implement`, where `--head` is the commit the task builds on (the ledger base, then the previous task's commit). The tool refuses any other checkout, refuses a dirty checkout (discard a failed run's writes first) and fails a task that flipped a modified file's line endings; the lane checks none of these (2026-09-22). The tool copies the brief into the checkout, runs agy with the closing line that keeps the test and commit steps off Gemini, deletes the copy, writes `build\task-NN-report.md` and prints the success test. The session reads that, never agy's exit code.
4. **The session checks the task itself before the next**: run the task's tests in the background (a Gemini task's first run, since print mode runs no command; red-then-green is observed only on the `backup-implementer` lane); read the diff against the task's files and its fenced code; then make the task's commit with the task's own commit step. The session is the one commit owner on both lanes. No per-task reviewer subagent.
5. Ledger line: the task's commit and result, with the lane that built it.

## To the `backup-implementer` instead

Dispatch `agents/backup-implementer.md` (Opus 5.5 at `medium`) in the background, named `Task N Implement`, with the brief path, the contract path (`templates/implementer-contract.md`), the checkout and a report path, for:

- a task that deletes, renames or moves a file (print mode has no delete tool, measured 2026-09-22);
- a task whose Gemini run failed the success test once, or whose diff did not match its code (below);
- every task when the pre-flight finds no agy.

Run `build archive --feature <folder> --task N` before ANY redispatch of a task that already has a report, so no attempt's evidence is overwritten. The `backup-implementer` reports blocked itself.

## A failing task

A task whose CODE is wrong is the author's defect. Gemini never reports blocked (2026-09-22: it read two errors on the missing dependency it was told to dot-source, edited on and reported success), so on that lane the failed test run is the signal, and the session names the cause in this order:

1. **The diff does not match the task's code**: a transcription failure. The task goes to the `backup-implementer` as its second dispatch.
2. **The diff matches**: check the base first. The checkout must sit at the previous task's commit and every file the task consumes must exist (the 2026-09-22 wrong-base run had transcribed its edits exactly on a checkout one commit too early). A wrong base is the session's to fix before it dispatches the task again; that redispatch still counts.
3. **The base is right**: the task is wrong. The `author`, resumed, amends it; `verify --feature <folder> --record-amendment "<reason>"` records it; the gate's `context.md` lists it. No extra round unless the amendment changes something another task consumes; then Brandon is asked.

A second failed dispatch of the same task, for ANY reason, amendment cycles included, goes to Brandon. A debate pauses after five rounds of one lane and kind; the build loop's stop is this rule.

## After a compaction

A `task-NN-brief.md` with no `task-NN-report.md` beside it means a build may still be running, on either lane. Check the background task list before dispatching that task again (undated).

## The gate and the finish

Then the diff gate (`debate`, `--kind diff`, with the pre-review first and the last look after), then the finish. The plugin's part of the order is one sentence: the gate runs first, the project's human check (a smoke, on Brandon's yes) last, on the final head.

The finish is STOP AND REPORT unless Brandon, a handoff or the project's finishing rule says merge or pull request. The report takes the shape and destination the handoff or project gives, and lists every open Minor finding, every refutation the driver made and every round it closed on Minor findings, each with its reply path, so nothing decided on Brandon's behalf is silently dropped. A degraded gate blocks a clean report. Only the commit the final PASS names is merged.

## Ledger lines this skill writes

Each task's commit and result with the lane that built it; whether it made the worktree; the finish.
