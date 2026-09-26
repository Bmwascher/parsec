# GPT-6 Sol (`gpt-6-sol`)

The default codex lane from 2026-09-22 (Brandon's word). Same CLI, flags and brief shape as Astra; only the id in `lanes.toml` differs.

## Dated facts

- The id answers only on codex 0.156.0 or newer (2026-09-22; `codex-cli.md`, "A missing model is a stale CLI first").
- Probe at effort `high`: `ready GPT-6`, 9,875 tokens for one word (2026-09-22). The cache lists its default effort as `medium` and no effort ladder; `high` is the lane's starting point, as for Astra.

## Carried from GPT-5.6 Sol, UNMEASURED on GPT-6

- "A higher effort spread to its subagents and burnt tokens" (old notes, UNDATED); fast tier at 1.5x (the catalog, 2026-09-22).

## Measured here

- 2026-09-22, `high`, fresh: a diff round in 338 s (Astra 153 s), same verdict and findings plus one Astra missed; a blind panel in 716 s (Astra 464 s), same winner, one defect Astra missed. Slower, reads more.
- KitnEssentials, 2026-09-22 to 25: every resume answered continuity; 93k to 113k tokens a round; `rg` in 15 of 27 transcripts; once, draft reasoning after its verdict.
