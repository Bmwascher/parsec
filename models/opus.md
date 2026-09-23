# Claude Opus 5.5 (`claude-opus-5-5`)

The `author` seat (from 2026-09-22), the `reviewer-opus` seat (the pre-review) and the `backup-implementer` seat.

## The guide says, so the plugin does

The bundled Claude API reference (cached 2026-06-24): Opus 5.5 succeeds Opus 5 at a lower price; its default effort is `medium`, so every seat pins its effort; thinking cannot be turned off, so effort is the only depth control. The Opus 5 guide (2026-09-21): start the pre-review at `high`; Opus obeys "report only what matters" literally and under-reports, so every brief says "report everything found, graded" (`templates/brief.md`). Both carry to 5.5 until measured.

Claude Code below 2.1.280 rejects the id with a 400 that names the version (seen 2026-09-22 on 2.1.277); the desktop app and an updated CLI take it.

## Measured here, on Opus 5

- **Implementer, Task 2 of the comparison, 2026-09-22, effort `medium`**: byte-identical to the reference edit in 370 s over 8 turns (Sonnet 5 took 48 turns for the same result), with its own fail-first step and the sharpest report; list cost under $0.89 merged with the driver's turn. Brandon chose it over Sonnet 5 at `medium`.
- Untested on the broken base (a checkout one commit too early), where Sonnet blocked in 53 s (2026-09-22).

## Measured here, on Opus 5.5

- **Author, 2026-09-22, effort `high`, headless**: spec 402 s (about $3.0 list); task list resumed, 634 s (about $6.6 list). A blind Astra plus Sol 6 panel ranked the pair first on four axes of five against the Fable pair and the real superpowers pair; its first three tasks built green on the Gemini lane.

## Unmeasured

- The backup-implementer at `medium` and the pre-review at `high` on 5.5.
- Effort per task: one effort per seat, by design.
