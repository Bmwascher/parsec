# GPT-6 Sol (`gpt-6-sol`)

The default codex lane from 2026-09-22 (Brandon's word; Astra is the alternate by name). Same CLI, flags and brief shape as Astra; only the id in `lanes.toml` differs. Moved from `gpt-5.6-sol` the day GPT-6 Sol released.

## Dated facts

- The id answers only on codex 0.156.0 or newer: on 0.153.4 the server said `The 'gpt-6-sol' model is not supported when using Codex with a ChatGPT account` and the CLI's model cache did not list it; `npm install -g @openai/codex@latest` fixed both (2026-09-22; `codex-cli.md`, "A missing model is a stale CLI first").
- Probe at effort `high`: `ready GPT-6`, 9,875 tokens for one word (2026-09-22). The cache lists its default effort as `medium` and no effort ladder; `high` is the lane's starting point, as for Astra.
- The tier-gating 400 was first seen on the 5.6 id (2026-07-12; `codex-cli.md`); not yet seen on GPT-6 Sol.

## Carried from GPT-5.6 Sol, UNMEASURED on GPT-6

- "A higher effort spread to its subagents and burnt tokens" (old notes, UNDATED); fast tier at 1.5x (the catalog, 2026-09-22).

## Measured here

- 2026-09-22, `high`, fresh: a diff round in 338 s (Astra 153 s), same verdict and findings plus one Astra missed; a blind panel in 716 s (Astra 464 s), same winner, one defect Astra missed. Slower, reads more.

## Unmeasured

Continuity across resumes and token use per round.
