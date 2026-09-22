# GPT-6 Sol (`gpt-6-sol`)

The alternate codex lane, used when Brandon says so or the config's `codex_lane` names it. Same CLI, same flags, same brief shape as Astra; only the id in `lanes.toml` differs. The row moved from GPT-5.6 Sol (`gpt-5.6-sol`) to GPT-6 Sol on Brandon's word the day it released (2026-09-22); whether Sol becomes the primary lane with Astra as the alternate for projects that need it is Brandon's decision, pending the first measurements below.

## Dated facts

- The id answers only on codex 0.156.0 or newer: on 0.153.4 the server said `The 'gpt-6-sol' model is not supported when using Codex with a ChatGPT account` and the CLI's model cache did not list it; `npm install -g @openai/codex@latest` fixed both (2026-09-22; `codex-cli.md`, "A missing model is a stale CLI first").
- Probe at effort `high`: `ready GPT-6`, 9,875 tokens for one word (2026-09-22). The cache lists its default effort as `medium` and no effort ladder; `high` is the lane's starting point, as for Astra.
- The tier-gating 400 was first seen on the 5.6 id (2026-07-12; `codex-cli.md`); not yet seen on GPT-6 Sol.

## Carried from GPT-5.6 Sol, UNMEASURED on GPT-6

- "A higher effort spread to its subagents and burnt tokens" (old notes, UNDATED).
- Fast tier at 1.5x speed (the catalog, read 2026-09-22).

## Unmeasured

Everything the rethink measured on Astra: continuity across resumes, round times, token use per round. The first diff round on this id (the totem-extent range, 2026-09-22) is recorded in the rethink's measurements file once it lands here.
