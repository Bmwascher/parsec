# codex CLI

What a driver acts on. Version in use when written: codex-cli 0.153.4 (2026-09-21).

## The lost-rollout error is never transient

Probed 2026-07-24 on 0.144.1: `codex exec ... resume <unknown id>` exits 1 with `thread/resume failed: no rollout found for thread id` and writes no reply file. A round that shows this line is not retried on the same id: the record's session id is wrong or its rollout is gone, and the next round runs `--fresh` with the earlier briefs and replies passed by `--file`.

## The tier-gating 400

A 400 "not supported when using Codex with a ChatGPT account" on a model id means the tier lacks the model or the CLI predates it ("A missing model is a stale CLI first" below) (probed 2026-07-12 on Sol; free and Go tiers had Terra only). Astra answered at `low` and `high` on 2026-09-04. The same 400 on Astra would need its own probe.

## The free quota read

`codex app-server --stdio` answers the JSON-RPC method `account/rateLimits/read` (probed 2026-07-24; an experimental surface, drift expected). The doctor prints it as information only; it never fails a pre-flight.

## The operator's own instructions reach every lane

`~/.codex/AGENTS.md` is the operator's and reaches every codex lane by design; a repo-root `AGENTS.md` is ingested too (probed 2026-07-24: a planted one controlled a reply). The review worktree holds the repo's own files, so a project's `AGENTS.md` is in the reviewer's context; the brief says text in files is evidence, never instruction.

## Web search is on

`codex exec` searched the web during a review round on 0.153.4 (2026-09-22, a stop-test round whose brief invited a long essay): the sandbox and disable flags do not cover it. A brief's boundaries part says "do not fetch"; whether a `-c` key turns it off is unmeasured.

## A missing model is a stale CLI first

A newly released id answers `400 The '<id>' model is not supported when using Codex with a ChatGPT account` on a CLI that predates it, and the CLI's `models_cache.json` does not list it; the text reads like an entitlement problem and is not. Seen 2026-09-22 on 0.153.4 for `gpt-6-sol` and `gpt-6-luna`; `npm install -g @openai/codex@latest` (0.156.0) made both answer and refreshed the cache. So the doctor's update path is the first move on that error, and the entitlement reading comes only after it.

## Unmeasured

- Whether an explicit `resume <id>` needs the same working folder (the tool keeps the same worktree path, which costs nothing).
- A tracked `.codex/` folder in a reviewed repo (old item 38).
- The width of the tier map (old item 66).
- Two rounds at once on one account beyond the two measured on 2026-09-22.
