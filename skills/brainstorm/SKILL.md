---
name: brainstorm
description: Use when Brandon says "brainstorm", "design" or "plan" a feature, or hands over a phase or handoff to build. The conversation and the orchestration from a request to an approved spec, an approved task list, a recorded go and one pre-build debate. Not for a bug fix that needs no design (that is bounded work, see the classification).
---

# brainstorm

Rules that cut across the flow are in `${CLAUDE_PLUGIN_ROOT}/templates/driver-rules.md`; read it first. The FORMAT of the two files is not here: it is in `templates/spec.md` and `templates/task-list.md`, read by whoever writes.

## Classify the request out loud

Say which it is before anything else. It only ever gets heavier, never lighter.

- **Spike**: exploration with nothing to keep. No feature folder, no spec, no debate. Say what was learned and stop.
- **Bounded work**: a change small enough to make without a design (a fix, a rename, a guard). No spec, no task list. Brandon's yes is the go; the session builds and commits it, then runs the diff gate (`build`, "Bounded work").
- **Architectural**: everything else. The full flow below.

## What is asked, and what is not

A handoff that settles the design replaces the interview. Read from what the session was handed: branch, base, checkout, whether the plan is pre-approved, the finish rule ("you do not merge"), and where to report. Record them in the ledger and ask only for what is missing. Otherwise interview:

- One question at a time, multiple choice where possible.
- Two or three approaches with a recommendation and the reasons.
- The design presented in sections, approval on each.
- A published page when a question is clearer shown than described (rule 4).

YAGNI; design for isolation; follow the patterns already in the code; no unrelated refactoring; split a request that is really several subsystems into several features.

## The feature folder

Made when the request is classified as architectural and named, one folder per feature; its name and layout are `setup`'s "Feature folder" and "Inside it" rows.

## Who writes

Keep `notes.md` as a running record: each question, Brandon's exact answer, the chosen approach and what was rejected, verbatim, never a digest. Then dispatch the `author` (`agents/author.md`) in the background, named `Author: spec`, with the notes (or the handoff and its scoping section), the code paths and the same context paths a reviewer gets (the config's `[[context]]` entries), asking for the spec alone.

The session never writes the two files itself: the author's fresh context proves the notes complete and keeps the session small.

Brandon reviews the written spec before the task list, from its decision summary posted in chat (a delegator relays it), even under a pre-approved handoff: "It shouldn't be taken as gospel basically and still should be reviewed and go through the gates" (2026-09-23). Approving the spec is not a go. After approval, the same `author` agent, resumed, writes the task list (`Author: task list`).

## The go (its one home)

Nothing is built without one. When the task list exists, the driver asks for it, before the first debate round: "Go?" A pre-approved handoff is already a go to build, never approval of the spec; a go given earlier in the conversation is recorded when it is given. The ledger line: `templates/ledger.md`.

## The pre-build debate

One debate over both files, `--kind design`, run by `debate` on the cross-vendor lane, then the Fable design look (`debate`, "The Fable looks"). When both end, the driver posts what they changed and:

- continues to `build` if a go is on record and neither changed what the feature does;
- pauses and asks when no go is on record, or when either changed what the feature does (a new behaviour, a dropped one, a different interface).

## Ledger lines this skill writes

Shapes in `templates/ledger.md`: the head (the base is written here, once, and nowhere else), the handoff facts, the go.

## Running the tool

The tool is `${CLAUDE_PLUGIN_ROOT}/tools/parsec.py`, run with `python`. `brainstorm` itself runs none of its subcommands; `debate` runs the rounds and `build` runs `verify`.

## Known clashes, not fixed

- "Spec" means the design document here and a busted test file in the projects. Noted, not renamed.
- `brainstorm` never promises a clean run of the project's plan linter, which ignores the project's luacheck config (measured 2026-09-21).
