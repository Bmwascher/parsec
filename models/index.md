# The models set

One file per CLI and per model, holding only what a driver acts on, each fact dated or marked UNMEASURED. CLI facts the tool enforces (the flags before `resume`, the disable flags, the cleared variable, never `--last`) are NOT here: each lives as a dated comment beside the argument list in `tools/parsec.py` and in its test's name.

## Seats

| Seat | Read | Where the id and effort live |
|---|---|---|
| `author` | `fable.md` | `agents/author.md` |
| `implementer` | `opus.md`, `templates/implementer-contract.md` | `agents/implementer.md` |
| Build lane (Gemini) | `agy-cli.md` | `lanes.toml`, row `gemini` |
| `reviewer-opus` | `opus.md` | `agents/reviewer-opus.md` |
| `reviewer-fable` | `fable.md` | `agents/reviewer-fable.md` |
| Astra lane | `codex-cli.md`, `astra.md` | `lanes.toml`, row `astra` |
| Sol lane (alternate) | `codex-cli.md`, `sol.md` | `lanes.toml`, row `sol` |
| Kimi lane (backup) | `kimi-cli.md`, `kimi-k3.md` | `lanes.toml`, row `kimi`; effort in the lane home |
| Driver | nothing here | the session's own model; not pinned by the plugin |

## Seat-invariant rules

- Ground every claim in what was run: a command, a file, a line. A claim without that is struck from a brief and from a report.
- State what is out of scope, in the brief and in the reply.
- A fresh context reviews better than self-critique: the last look is a fresh agent, and a confirming question resumes it only about its own finding.
- The brief shape is `templates/brief.md`; nothing here restates it.

## Citations

Every note cites a heading or a date, never `path:line`: six such citations went stale in the old notes (old item 69).

## Swapping a model

1. Effort names do not mean the same amount of thinking across models: every swap re-decides the seat's effort from that model's own guide, and records the starting point here.
2. Pin the full id in the agent file or `lanes.toml`; what an alias resolves to was never measured (old item 81).
3. Run the pre-flight on the new lane before a round is spent.
4. Add the model's file here, with its guide's URL and fetch date, and what is unmeasured.
5. Re-measure the effort claims that the old model's file carried; a claim does not transfer.
