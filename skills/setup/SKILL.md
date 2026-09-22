---
name: setup
description: Use once per project, and again after a folder move or a PC reset, to write the parsec config (`.claude/parsec.toml`) in the primary checkout; also when the tool says "run setup first".
---

# setup

The config holds ONLY what the tool or the `debate` skill reads as data. Gates, plan lint, smoke rules, merge or PR policy, commit style, test policy and retention stay as prose in the project's own rules.

## Settled rules

| Point | Rule |
|---|---|
| Config home | One file in the PRIMARY checkout, `.claude/parsec.toml`, always read from the primary; a worktree's stale copy is never read. |
| No config yet | The tool exits 64, "run setup first". |
| Guess first, then confirm | Scan the repo with file tools and two read-only git commands, `git worktree list` and `git check-ignore`; show ONE proposed config with the evidence for each guess; Brandon corrects by exception; write nothing before he confirms. Look at: existing `docs` folders and whether git ignores them; the worktree list; `AGENTS.md` and `CLAUDE.md` in the repo and in the folders above it, up to the first folder that holds neither, with their headings listed for the section pick; links at the repo root and a `References` folder; the old-plugin lines the adoption-day list names (printed, never edited). |
| Required | Only `docs_root` and `worktrees`. |
| Not applicable | `[reviewer]` defaults to `sol` and `ask` when unanswered. A `[[context]]` question may be answered "N/A", "none", "skip" or anything that means the same (a model reads the answer; no phrase list is parsed); record it as `context = []`, so a later run can tell "answered none" from "never asked". With no rubric the brief has no rubric part and the pre-flight prints `rubric: none configured`. |
| Tracked docs root | Warn when git tracks the docs root: round replies committed into the reviewed tree once ended a panel's blindness (old item 49). Round folders are then not committed while a debate or panel is open. |
| Feature folder | `<docs-root>\<MM-DD>-<topic>\`, no year; the year and the readable title sit at the top of the notes and the ledger's head. `<project>`, wherever a worktree name uses it, is the primary checkout's folder name. |
| Inside it | Loose: `notes.md`, `spec.md`, `tasks.md`, `ledger.md`. Subfolders made when their first file is written: `rounds\`, `build\` (`task-NN-brief.md`, `task-NN-report.md`, `task-NN-agy.log`), `pages\`. |
| Panels about no feature | `<docs-root>\panels\<MM-DD>-<topic>\`, the one feature folder the tool makes itself. |
| Machine paths | Absolute paths are allowed (the worktrees folder; a rubric above the repo); relative paths resolve against the primary. After a PC reset or a folder move, run setup again. |
| Old superpowers documents | Left where they are; nothing is migrated. |
| Levels | No user-level defaults file. Each project answers once. |

## Worked example

```toml
# .claude/parsec.toml  (primary checkout; .claude is gitignored here)
docs_root = "dev/docs/parsec"
worktrees = "C:/Users/Brandon/Documents/KitnDev/_worktrees"

[reviewer]                       # optional; these are the defaults
codex_lane        = "sol"        # or "astra"; the lane a round takes when --lane is omitted
kimi_substitution = "ask"        # or "approved"

[[context]]                      # read first: the reviewer's rubric
path     = "C:/Users/Brandon/Documents/KitnDev/AGENTS.md"
role     = "rubric"
sections = ["Lua style (shared)", "Git"]

[[context]]
path     = "AGENTS.md"           # relative: the primary checkout
role     = "rubric"
sections = ["Performance", "Verification"]

[[context]]                      # look up and cite, never required reading
path = ".wow-api-reference"      # a link: resolved to its real target once
role = "lookup"

[[context]]                      # named in a brief with --reference
path = "References"
role = "reference-code"
```

A section is matched by exact heading text at any `#` level; a missing one stops the pre-flight before a round is spent.
