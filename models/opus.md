# Claude Opus 5 (`claude-opus-5`)

The `reviewer-opus` seat (the pre-review) and the `implementer` seat (the build fallback); also the usual driver.

## The guide says, so the brief carries

Opus 5 guide, fetched 2026-09-21: start the pre-review at effort `high`. Opus obeys "report only what matters" literally and under-reports, so every brief says "report everything found, graded, never only the severe ones" (`templates/brief.md`).

## Measured here

- **Implementer, Task 2 of the comparison, 2026-09-22, effort `medium`**: byte-identical to the reference edit in 370 s over 8 turns (Sonnet 5 took 48 turns for the same result), with its own fail-first step and the sharpest report; list cost under $0.89 merged with the driver's turn; the 5-hour window moved 3 points. Brandon chose it over Sonnet 5 at `medium` (09:53 CDT).
- Untested on the broken base (a checkout one commit too early), where Sonnet blocked in 53 s.
- Token accounting for a headless `claude -p --output-format stream-json` run: the result event's `modelUsage` per model is the spend, subagent included; the top-level `usage` is the driver turn only; per-turn `output_tokens` is message-start and useless (2026-09-22).

## Unmeasured

- The pre-review seat at `high` on a real diff package (no measurement yet; the guide's starting point).
- Effort per task: one effort per seat, by design.
