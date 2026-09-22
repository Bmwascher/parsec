# Claude Fable 5.1 (`claude-fable-5-1`)

The `reviewer-fable` seat: the last look on both halves, a panel lane, an adjudication and a poll. The `author` seat moved to Opus 5.5 on 2026-09-22 after a blind panel ranked the Opus pair above the Fable pair on fidelity, correctness, tests and buildability (`opus.md`).

## The guide says, so the plugin does

Fable 5.1 guide, fetched 2026-09-21: start at effort `high` for authoring and review; raise only on a measured gain. Its warning that higher efforts draft a long deliverable twice is the guide's claim, UNMEASURED here.

## Measured here

- Five fresh reviews of the rethink's design files (2026-09-21) and five more in the tandem review (2026-09-22): every one returned FIX with cited findings, several of them the same defects Astra found independently (convergent), and one design defect Astra missed (the deleted-key rows in the setup draft).
- A background reviewer agent read files above the primary checkout and wrote its report file with no permission stop (five reviews, 2026-09-21): one data point for the in-session design; owed item 13 re-checks it under the shipped plugin.
- A finished agent's output file measured 0 bytes on 2026-09-21, so the report is written by the agent itself, never copied out of its reply.

## Unmeasured

- Authoring: owed item 12 measures Opus and Fable each writing the round tool's spec and task list from the same notes, with an Astra round 1 on each.
- Effort `medium` on either seat.
