---
name: build
description: Use when a designed feature has a go on record and is to be built, or when bounded work has Brandon's yes. The session builds from the spec, test first, commits each step, then runs the diff gate and finishes as the project's rule says.
---

# build

Rules that cut across the flow are in `${CLAUDE_PLUGIN_ROOT}/templates/driver-rules.md`; read it first. The tool is `${CLAUDE_PLUGIN_ROOT}/tools/parsec.py`, run with `python`; its `--help` carries the argument detail.

## Start

- Refuse to start without a recorded go (`brainstorm`), or without a design look after the last cross-vendor design round: a `design r<n> fable` ledger line, or, on Brandon's `waiver` ledger line for the stand-in, an Opus stand-in's `design r<n> opus` line (`debate`, "The Fable looks").
- Run `verify --feature <folder>`: MATCH and MATCH (CLOSED ON MINOR) continue; MATCH (DEGRADED PASS) and CHANGED stop and ask Brandon; NO-PASS-YET refuses.
- Read the base from the ledger head (written once, by `brainstorm`). A fresh worktree lacks the project's gitignored hook inputs (KitnEssentials: `dev\githooks\upstream-names.local.sh`); copy them before the first commit (2026-09-22). Work in the checkout the session was handed, or make one at `<worktrees>\<Project>-<branch>` and record in the ledger that `build` made it. Only the checkout `build` made is ever removed by it, by `remove-worktree <checkout>` run from outside it, which unlinks the junctions `git worktree remove` leaves (2026-10-17), and never under stop and report.

## Bounded work

Skips the above: no `verify`; Brandon's yes is the go; the session builds, commits, then runs the gate (`debate`, `--kind diff`). The session answers a BLOCKING code finding there directly (no `author`), under the code rules below, and the next round runs on the answer's head (2026-09-28).

Its class is checked out loud first (`brainstorm`); a claim it rests on is probed first (driver rule 7).

**A small change** passes the gate with no cross-vendor round when a reader can judge it right from the diff alone (values, labels, renames, a new entry in an existing table, a copy of a pattern already in the same file); it has 20 or fewer changed lines (`git diff --numstat <base>..<head>`, added plus removed) in 2 or fewer files, test files counted in the lines but not the files; it adds or changes no game API call, hook, event handler or timing; and no Opus pre-review round on it found a Critical or Important. After the pre-review ends (a PASS, or a FIX closed on Minor), the driver checks each point and writes the `small` ledger line; a delegator never makes this call for a phase chat. The Fable last look still runs, and its posted summary and the finish report say `small: no cross-vendor round` (Brandon, 2026-10-15). A Critical or Important in that last look makes the change not small: after the answer, the cross-vendor round runs on the answer's head, then the last look's confirming question (Brandon, 2026-10-16).

## The session's build

1. **At the start of every step**, before its first edit, check that the checkout's `HEAD` is the expected commit: the commit of the newest `step NN:` ledger line; with none, of the newest `task NN:` line (a feature part-built under 0.1.54; the `build task NN` tool line is not read); with neither, the ledger base. In the same check `git status --porcelain --untracked-files=all`, run in the checkout, lists no entry but those under the docs-root prefix: the configured docs root's path relative to the checkout, or, when it lies under the primary checkout instead, relative to the primary, and only when the docs root is a strict subfolder of that tree; a docs root that is the whole tree, or outside both, exempts nothing. On another commit or any other entry (another phase's edit), stop and ask Brandon; never discard, stash or commit that entry. This holds after a compaction and when another phase sharing the checkout has committed between steps. Note the commit found as the step's start commit.
2. **Before the first code edit**, write `build\cases.md` in the feature folder: each Behaviour case of the spec with the test that will cover it, or the named check that stands in (its Testing section). It is not a review subject.
3. **Each step is one coherent change one commit holds.** Write the failing test, run it and see the expected failure (red), write the code, run it green, then run the whole suite, output clean. Before the commit check the branch (phase chats share a checkout) and that `HEAD` is still the step's start commit; if another phase moved it, run the whole suite again on the new head before committing, or stop and ask Brandon. Commit in the project's style. A step with nothing worth testing under the project's test policy names its check and is logged `green` with the reason. A check never runs a discarding git command. Only what the spec asks for; a second copy of a rule or helper is a defect. The project's test policy outranks these.
4. **Each commit gets a ledger line**: `step NN: <commit>, <tests: red then green | green: <reason>>`.
5. **Subagents read only.** An Explore or general-purpose subagent may read code for the session; no subagent writes code, a test or the spec. No per-step reviewer subagent.
6. **When the code proves the spec wrong**, the session alone edits only its Design section (a file, name, signature or call site). An edit to any other section (Goal, Approach, Behaviour, Testing; the two clerical edits of `brainstorm` apart), such as a case that cannot work as written, a new or dropped behaviour, a different interface or a changed expected result, pauses and asks Brandon before it is made. Each edit rewrites the affected section as it now stands, then re-checks the decision summary and every Goal and Behaviour sentence that touches the changed mechanism; one that no longer holds is edited only on Brandon's word. Then `verify --feature <folder> --record-amendment "<reason>"` runs before the next round is prepared; the gate's `context.md` lists it.
7. **Gate findings.** An unrefuted Critical or Important code finding at any point of the diff gate, and a Minor triaged to fix in code, is fixed by the session and committed as a step under 1, 3 and 4; the next round runs on the new head. A fix that changes what `spec.md` states amends it under 6. A fix that changes what the feature does pauses and asks Brandon first.
8. **After a compaction**, the ledger's step lines, `git log <base>..HEAD` and `build\cases.md` show where the build stands.

## Code rules

For every line the session writes, in a build step, bounded work or a gate fix. A fix covers every site of its pattern, or every input order for logic, with a cited trigger, or names those left open for Brandon; a finding whose trigger does not hold is refuted as not reachable, with cited evidence, and gets no code and no test. A guard, or a branch, deferral, mode or helper for one case, needs a reason the code can name: a documented failure or empty return; data from outside the code, such as saved or imported data, a program the feature does not require, or user input; a call a supported platform may lack; or a hazard the project's rules name. A program or library the feature requires is code to read: guard only what its source shows can fail, or what a named hazard reaches. Other code runs unguarded, so a real failure is reported, not hidden.

## The gate and the finish

Then the diff gate (`debate`, `--kind diff`), then the finish. The gate runs first, the project's human check (a smoke, on Brandon's yes) last, on the final head. A commit other than a gate fix or the release's version bump, which the last look reviews, added after the pre-review was packaged, restarts the gate on the new head. A fix for a symptom seen in game passes `--reference` when its module was ported (`debate`), and its gate summary says the PASS covers the code, not the symptom: the smoke decides.

The finish is STOP AND REPORT unless Brandon, a handoff or the project's finishing rule says merge or pull request. The report takes the shape and destination the handoff or project gives, and lists every open Minor finding, every refutation the driver made and every round it closed on Minor findings, each with its reply path, then every "Open, not ruled" item, every site left open for Brandon, each spec amendment made during the build and the gate with its reason, and every delegated decision, for him to confirm or reverse, so nothing decided on Brandon's behalf is silently dropped, and carries `summaries.md` whole and, unless he approved the spec himself, the decision summary, which a delegator's relay keeps (2026-09-28). A degraded gate blocks a clean report. Only the commit the final PASS names is merged.

A rebased head counts as the commit the final PASS names only when `git patch-id --stable` gives the same id for the passed range and the rebased one, and the project's checks are green on it; otherwise the last look runs again on it. A worktree the session made by hand for a review or a check, not the checkout `build` made (Start), is removed by `remove-worktree`, run from outside it, when its step ends.

## Ledger lines this skill writes

Each build step line, the worktree line (Start), the small line (Bounded work), each probe result or claim waiver (driver rule 7, Bounded work), each gate result, the smoke, the finish.
