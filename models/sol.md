# GPT-6.1 Sol (`gpt-6.1-sol`)

The default codex lane from 2026-09-22 (Brandon's word); GPT-6.1 from 2026-09-30 (was `gpt-6-sol`). Same CLI, flags and brief shape as Astra; only the id in `lanes.toml` differs.

## Dated facts

- The id answers on codex 0.159.2 (2026-09-30). GPT-6 Sol needed 0.156.0 or newer (2026-09-22; `codex-cli.md`, "A missing model is a stale CLI first").
- Probe at effort `high`: `ready GPT-6`, 8,077 tokens for one word (2026-09-30; GPT-6 Sol 9,875 on 2026-09-22). The cache lists its default effort as `low` and efforts `low` to `max`; OpenAI's model page says `medium` (both read 2026-09-30). `high` stays the lane's starting point, as for Astra.
- Vendor guide: none for 6.1 (2026-09-30). OpenAI's GPT-6 guide (developers.openai.com/api/docs/guides/latest-model, fetched 2026-09-30) gives only the efforts and says to compare it with Astra on your tasks; its best practices describe Astra.

## Carried from GPT-6 Sol, UNMEASURED on GPT-6.1

- 2026-09-22, `high`, fresh: a diff round in 338 s (Astra 153 s), same verdict and findings plus one Astra missed; a blind panel in 716 s (Astra 464 s), same winner, one defect Astra missed. Slower, reads more.
- KitnEssentials, 2026-09-22 to 25: every resume answered continuity; 93k to 113k tokens a round (phase 14); `rg` against the lane line in 15 of 27 transcripts; once, draft reasoning after its verdict.
- From GPT-5.6 Sol, never measured on GPT-6: "A higher effort spread to its subagents and burnt tokens" (old notes, UNDATED); fast tier at 1.5x (the catalog, 2026-09-22).

## Measured here

- Nothing yet on GPT-6.1 beyond the probe.
