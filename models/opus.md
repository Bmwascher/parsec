# Claude Opus 5.5 (`claude-opus-5-5`)

The `author` seat (from 2026-09-22), the `reviewer-opus` seat (the pre-review) and the `implementer` seat (the build fallback); also Brandon's daily driver from 2026-09-22. The author is dispatched even though the driver is the same model: its fresh context is the point, not the model. Both seats moved from Opus 5 (`claude-opus-5`) to Opus 5.5 on Brandon's word the day it released (2026-09-22); the measurements below were taken on Opus 5 and carry as starting points, UNMEASURED on 5.5.

## The guide says, so the plugin does

From the Claude API reference bundled with Claude Code (cached 2026-06-24, read 2026-09-22): Opus 5.5 succeeds Opus 5 in the Opus line at a lower price; its default effort is `medium`, one level below Opus 5's `high`, so every seat pins its effort explicitly; thinking cannot be turned off, so effort is the only depth control. The Opus 5 guide (fetched 2026-09-21) said to start the pre-review at `high`, and that Opus obeys "report only what matters" literally and under-reports, so every brief says "report everything found, graded, never only the severe ones" (`templates/brief.md`). Both carry to 5.5 until measured.

Claude Code below 2.1.280 rejects the id with a 400 that names the version (seen 2026-09-22 on 2.1.277); the desktop app and an updated CLI take it.

## Measured here, on Opus 5

- **Implementer, Task 2 of the comparison, 2026-09-22, effort `medium`**: byte-identical to the reference edit in 370 s over 8 turns (Sonnet 5 took 48 turns for the same result), with its own fail-first step and the sharpest report; list cost under $0.89 merged with the driver's turn. Brandon chose it over Sonnet 5 at `medium` (09:53 CDT).
- Untested on the broken base (a checkout one commit too early), where Sonnet blocked in 53 s.
- Token accounting for a headless `claude -p --output-format stream-json` run: the result event's `modelUsage` per model is the spend, subagent included; the top-level `usage` is the driver turn only; per-turn `output_tokens` is message-start and useless (2026-09-22).

## Measured here, on Opus 5.5

- **Author, 2026-09-22, effort `high`, headless**: spec 402 s over 58 turns (42,496 out, 5.30 M cache read, about $3.0 list); task list resumed, 634 s over 25 turns (126,536 out, 10.08 M cache read, about $6.6 list). A blind Astra plus Sol 6 panel ranked the pair first on four axes of five against the Fable pair and the real superpowers pair; its first three tasks built green on the Gemini lane.

## Unmeasured

- The implementer at `medium` and the pre-review at `high` on 5.5.
- Effort per task: one effort per seat, by design.
