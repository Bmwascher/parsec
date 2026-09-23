---
name: debate
description: Use for every review round of the plugin's flow, the pre-build design debate, the diff gate (Opus pre-review, cross-vendor debate, Fable last look), and any time Brandon asks for a cross-vendor review of files or a branch. Runs the rounds through the tool, answers every finding, and closes under the debate's ending rules.
---

# debate

Rules that cut across the flow are in `${CLAUDE_PLUGIN_ROOT}/templates/driver-rules.md`; read it first. The tool is `${CLAUDE_PLUGIN_ROOT}/tools/parsec.py`, run with `python`; `--help` carries the argument detail.

## Running a round

- Run the pre-flight before round 1 and after a lane switch: `doctor --lane <lane> --kind <kind> --feature <folder>` (`--fast` too when the round will use it), in the background, and post its Markdown as is, outside a code block.
- Write the brief as `templates/brief.md` says, with the kind's insert.
- Start the round with Monitor, `timeout_ms` 1800000 (Monitor kills the script at expiry; the tool's own cap is 28 minutes), named before launch from the driver rules' list: `round run` for a CLI lane (`--lane` omitted: the config's `codex_lane`); `round prepare`, then the reviewer agent, then `round collect --agent-id <its id>` for opus or fable. `round prepare` prints the brief path, the code root (a review worktree at `--head`, for every lane), the report path and the task name for the dispatch.
- Pass `--fast` only on Brandon's explicit word for THAT debate ("use fast"), never from a config or an earlier debate.
- Pass `--reference <subfolder>` when the spec declares a port or touches a module that has a reference; a reference outside the reference-code folder goes in as `--file` evidence (field phase 6, 2026-09-23).
- Pass earlier briefs and replies with `--file` to a lane that joins mid-debate; its own rounds start at 1. The brief names each reply's lane and round.
- Post the summary after every round (every kind, a PASS included, and to a delegator too), without waiting for Brandon, as rendered Markdown in this shape. Never put it inside a code block: a fenced table wraps into unreadable pipes on his phone (2026-09-23).

  ```markdown
  ### 🔴 Astra R2 Design Round: FIX (7 min, resumed)
  **Needs you:** F4, contested twice. I recommend option a.

  Critical 0 · Important 2 · Minor 1

  Round 1: F1 closed · F2 reopened narrower · F4 still open

  - **F2 · Important (reopened):** <finding>.

    → **Fix:** <what changes>.
  - **F4 · Important (still open):** <finding>.

    → **You decide** (see above).
  - **F5 · Minor:** <finding>.

    → **Refute:** <evidence in a few words>.

  **Next:** author edits, then round 3.
  ```

  Every blank line in the shape is needed: a single line break renders as a space, which merges the lines.

  - The marker before the name: 🔴 FIX, 🟢 PASS, 🟡 ESCALATE or BLIND, ⚪ NONE or WROTE-FILES.
  - "Needs you" comes second and only when something waits on Brandon; leave it out otherwise.
  - Findings keep the reviewer's own IDs, so they match `reply.md` and the next round's "Round N" line, ordered by severity, then ID. A reply that gives no IDs is numbered F1, F2 and on in its own order, and the driver uses those numbers in every later round. A reopened or still-open finding says so in its bullet.
  - Every answer is **Fix** (what changes), **Refute** (the evidence in a few words) or **You decide**.
  - Only the verdict word is exact; the reviewer's own words stay in `reply.md`.
- Collect a round whose tool was killed (`round collect`), then rerun it on its session asking only for the verdict.
- Commit no round folder while the debate is open (`setup`, "Tracked docs root").
- `round close --feature <folder>` after the Fable last look passes (not after a stand-in or the diff debate's PASS), or on Brandon's word to stop.

## The rules of the debate

- **Answer every finding**: fix, refute with cited evidence, or escalate. The resumed `author` answers design findings, all of a round's in one resume, never ruled by the driver (Brandon, 2026-09-23); the driver checks every refutation against the source before it goes into a brief.
- **A BLOCKING code finding** (Critical or Important) at any point of the diff gate becomes a fix task written by the `author`, appended to `tasks.md`, recorded with `verify --feature <folder> --record-amendment "<reason>"` like any amendment, and built by the implementer; the next round runs on the new head. Bounded work: the session fixes it directly (`build`).
- **Continuity.** On `continuity: not answered`, or an answer that does not match the record (the question is `templates/brief.md`'s; compare the answer with `record.json` and that round's reply), the next round on that lane runs `--fresh` with the earlier briefs and replies passed by `--file`.
- **Adjudication.** When Opus drives, it may ask `reviewer-fable` to adjudicate before it refutes a Critical or Important finding, giving both positions as file paths in the feature folder; the call is poll-shaped (no report path, the answer in the reply, `Fable Poll`). The answer is advice; the twice-contested rule still applies.
- **The ending, stated once**: a debate ends on an ADJUDICATED DRY ROUND, no new Critical or Important finding and no contested point open. A PASS names its subject.
- **Minor and prose-only findings NEVER cost a round** (Brandon, 2026-09-21: code defects matter most, then tests; wording never earns a round of quota); only the reviewer grades a finding (2026-09-23: a driver closed an Important as wording). If a round still ends FIX and the reviewer graded every open finding Minor: fix them, run `round collect --feature <folder> --kind <kind> --round N --lane <lane> --close-minor "<reason>"`, say so in the round summary, and the debate is over. No confirming round, except for a last-look fix-now Minor ("The Fable looks"). After a design debate the edited files are recorded with `verify --feature <folder> --record-amendment "<reason>"`. In the diff gate such fixes are committed BEFORE the last look, which reviews the final head and so covers them. The finish report reads everything recorded (`build`).
- **After 5 rounds** of one lane and kind, it pauses and asks Brandon; a spent budget never certifies. A point contested twice with evidence on both sides goes to him at once, as does a finding family (one defect class under new IDs) reopened after two fixes: change the approach, or accept the residual (a `decision` ledger line).
- **A refusal on content grounds** is verdict NONE: reword in plainer terms and rerun under the same round number on the same session (old item 80).
- **If codex is unavailable**, ask before substituting Kimi, unless the config's `kimi_substitution` is `approved`. A debate finished on Kimi is a FULL gate with the lane switch recorded (consecutive round lines name their lanes). A gate run with no cross-vendor lane is degraded, never PASS: `round collect --feature <folder> --kind <kind> --round N --lane <lane> --degraded "<reason>"`.
- **The diff gate's order**: Opus pre-review (`--kind prereview`, `reviewer-opus`, round 1), the cross-vendor debate (`--kind diff`, also from round 1), the Fable last look (`--kind lastlook`). A Minor fixed in code during the gate also amends `spec.md` and `tasks.md` where they state the old behaviour, recorded with `verify --record-amendment`.
- **The Fable looks**: a FRESH `reviewer-fable`, briefed with the debate's shared text plus `templates/brief-lastlook.md`, gives the design look (`--kind design`, `--head` the ledger base) after the cross-vendor design debate, and the last look. A Critical or Important finding goes to the `author` (in the gate, also one confirming round on the debate's lane); then ONE confirming question, the next round of that kind sent to the same agent and prepared with `--resume <agent id>`, asks only about its own findings and its fix-now Minors; a second FIX goes to Brandon. Design-look Minors, even under a PASS, are fixed in one author resume and recorded with `verify --record-amendment`, no question. A last-look Minor triaged fix now is fixed, committed and covered by that one question even after a PASS, so the final PASS names the real head (Brandon, 2026-09-23); a ride Minor is recorded, not applied (old item 23). If Fable is unavailable, ask Brandon; never a silent stand-in. On his word (a `waiver` ledger line) Opus stands in (`--lane opus`), recorded degraded for a last look until a Fable one on the same head supersedes it.
- **Settled rules go to their durable home.** Before a debate closes, a rule that settled a contested point is written to the feature's notes or this plugin's model notes, so no later debate pays a round for it again (old item 37, undated). A rule that belongs in the project's `AGENTS.md` is proposed to Brandon and never written by the plugin.
- **Bounded work**: the diff debate makes the feature folder and its ledger, whose head records the base.

## What the tool records

Every round leaves `rounds\<kind>-r<n>-<lane>\` with the brief, the reply, `record.json` and one ledger line; a dead attempt is renamed `.dead<k>`. The tool never parses a ledger line it did not write, and the driver never retypes anything a model wrote into an argument: free text on a command line is a short plain phrase, no quotes or backticks.
