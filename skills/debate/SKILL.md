---
name: debate
description: Use for every review round of the plugin's flow, the pre-build design debate, the diff gate (Opus pre-review, cross-vendor debate, Fable last look), and any time Brandon asks for a cross-vendor review of files or a branch. Runs the rounds through the tool, answers every finding, and closes under the debate's ending rules.
---

# debate

Rules that cut across the flow are in `${CLAUDE_PLUGIN_ROOT}/templates/driver-rules.md`; read it first. The tool is `${CLAUDE_PLUGIN_ROOT}/tools/parsec.py`, run with `python`; `--help` carries the argument detail.

## Running a round

- Run the pre-flight before round 1 and after a lane switch: `doctor --lane <lane> --kind <kind> --feature <folder>` (`--fast` too when the round will use it), in the background, and post the block as is.
- Write the brief to a file WITH A FILE TOOL, never through a shell (2026-09-17: a heredoc lost every apostrophe and backtick while every check passed), from `templates/brief.md` with the kind's insert.
- Start the round with Monitor, `timeout_ms` 1800000 (Monitor kills the script at expiry; the tool's own cap is 28 minutes), named before launch from the driver rules' list: `round run` for a CLI lane (`--lane` omitted: the config's `codex_lane`); `round prepare`, then the reviewer agent, then `round collect` for opus or fable. `round prepare` prints the package root, the code root and its commit, the report path and the task name for the dispatch.
- Pass `--fast` only on Brandon's explicit word for THAT debate ("use fast"), never from a config or an earlier debate.
- Pass `--reference <subfolder>` when the spec declares a port or touches a module that has a reference.
- Pass earlier briefs and replies with `--file` to a lane that joins mid-debate; its own rounds start at 1.
- Post the summary after every round, in this shape, without waiting for Brandon:

  ```
  Astra R2 Design Round: FIX   (7 min, resumed)
  Critical 0, Important 2, Minor 1. Round 1's three findings: 2 closed, 1 still open.
  | # | Severity | Finding | My answer |
  Next: author edits, then round 3.
  ```

  Only the verdict word is exact; the reviewer's own words stay in `reply.md`. A refuted finding shows its evidence in a few words.
- Collect a round whose tool was killed (`round collect`), then rerun it on its session asking only for the verdict.
- Commit no round folder while the debate is open (`setup`, "Tracked docs root").
- `round close --feature <folder>` after the last look passes (not after the diff debate's PASS), or on Brandon's word to stop.

## The rules of the debate

- **Answer every finding**: fix, refute with cited evidence, or escalate. The resumed `author` answers design findings; the driver checks every refutation against the source before it goes into a brief.
- **A BLOCKING code finding** (Critical or Important) at any point of the diff gate becomes a fix task written by the `author`, appended to `tasks.md`, recorded with `verify --feature <folder> --record-amendment "<reason>"` like any amendment, and built by the implementer; the next round runs on the new head. Bounded work: the session fixes it directly (`build`). After the last look the loop is bounded: one confirming round on the debate's lane, and the same last-look agent is asked only about its own finding.
- **Continuity.** On `continuity: not answered`, or an answer that does not match the record (the question is `templates/brief.md`'s; compare the answer with `record.json` and that round's reply), the next round on that lane runs `--fresh` with the earlier briefs and replies passed by `--file`.
- **Adjudication.** When Opus drives, it may ask `reviewer-fable` to adjudicate before it refutes a Critical or Important finding, giving both positions as file paths in the feature folder; the call is poll-shaped (no report path, the answer in the reply, `Fable Poll`). The answer is advice; the twice-contested rule still applies.
- **The ending, stated once**: a debate ends on an ADJUDICATED DRY ROUND, no new Critical or Important finding and no contested point open. A PASS names its subject.
- **Minor and prose-only findings NEVER cost a round** (Brandon, 2026-09-21: code defects matter most, then tests; wording never earns a round of quota). If a round still ends FIX and every open finding is graded Minor, or touches only wording and no code, test, interface or behaviour: fix the wording, run `round collect --feature <folder> --kind <kind> --round N --lane <lane> --close-minor "<reason>"`, say so in the round summary, and the debate is over. No confirming round. After a design debate the edited files are recorded with `verify --feature <folder> --record-amendment "<reason>"`. In the diff gate such fixes are committed BEFORE the last look, which reviews the final head and so covers them; after the last look they are recorded, not applied, because any edit moves the head off the commit the PASS covers (old item 23). The finish report reads everything recorded (`build`).
- **After 5 rounds** it pauses and asks Brandon; a spent budget never certifies. A point contested twice with evidence on both sides goes to him at once.
- **A refusal on content grounds** is verdict NONE: reword in plainer terms and rerun under the same round number on the same session (old item 80).
- **If codex is unavailable**, ask before substituting Kimi, unless the config's `kimi_substitution` is `approved`. A debate finished on Kimi is a FULL gate with the lane switch recorded (consecutive round lines name their lanes). A gate run with no cross-vendor lane is degraded, never PASS: `round collect --feature <folder> --kind <kind> --round N --lane <lane> --degraded "<reason>"`.
- **The diff gate's order**: Opus pre-review (`--kind prereview`, `reviewer-opus`), the cross-vendor debate (`--kind diff`), the Fable last look (`--kind lastlook`) by a FRESH `reviewer-fable`; only the one confirming question about its own finding resumes that agent.
- **Settled rules go to their durable home.** Before a debate closes, a rule that settled a contested point is written to the feature's notes or this plugin's model notes, so no later debate pays a round for it again (old item 37, undated). A rule that belongs in the project's `AGENTS.md` is proposed to Brandon and never written by the plugin.
- **Bounded work**: the diff debate makes the feature folder and its ledger, whose head records the base.

## What the tool records

Every round leaves `rounds\<kind>-r<n>-<lane>\` with the brief, the reply, `record.json` and one ledger line; a dead attempt is renamed `.dead<k>`. The tool never parses a ledger line it did not write, and the driver never retypes anything a model wrote into an argument: free text on a command line is a short plain phrase, no quotes or backticks.
