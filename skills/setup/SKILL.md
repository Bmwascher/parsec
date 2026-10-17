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
| Guess first, then confirm | Scan the repo with file tools and two read-only git commands, `git worktree list` and `git check-ignore`; show ONE proposed config with the evidence for each guess; Brandon corrects by exception; write nothing before he confirms. Look at: the worktree list, for the worktrees folder and the docs root guess beside it ("Docs root"); existing in-repo `docs` folders, never the guess, and whether git ignores them ("Tracked docs root"); `AGENTS.md` and `CLAUDE.md` in the repo and in the folders above it, up to the first folder that holds neither, with their headings listed for the section pick; links at the repo root and a `References` folder. |
| Required | Only `docs_root` and `worktrees`. |
| Not applicable | `[reviewer]` defaults to `sol` and `ask` when unanswered. A `[[context]]` question may be answered "N/A", "none", "skip" or anything that means the same; record it as `context = []`, so a later run can tell "answered none" from "never asked". With no rubric the brief has no rubric part and the pre-flight prints `rubric none configured`. |
| Docs root | Outside the repo, beside the worktrees folder (`<parent>\_parsec\<project>`): the desktop app's worktree guard denies a worktree session's file tools, and its seats, any path in the primary checkout (2026-10-17, KitnUI). In the desktop app the pre-flight refuses a seat run from a worktree while the docs root is in the primary. |
| Tracked docs root | Warn when git tracks the docs root: round replies committed into the reviewed tree once ended a panel's blindness. Round folders are then not committed while a debate or panel is open. |
| Feature folder | `<docs-root>\<MM-DD>-<topic>\`, no year; the year and the readable title sit at the top of the notes and the ledger's head. One folder per feature: every file it writes, and any path a handoff gives for it, resolves inside it (field audit, 2026-09-23). The folder, the branch and the worktree share one `<topic>` when the plugin names them; names a handoff gives are recorded as given. `<project>`, wherever a worktree name uses it, is the primary checkout's folder name. |
| Inside it | Loose: `notes.md`, `spec.md`, `tasks.md`, `ledger.md`, the tool's `summaries.md`, and nothing else. Every other file goes in a subfolder named for what it holds, made when its first file is written: `rounds\`, `build\` (`task-NN-brief.md`, `task-NN-report.md`, `task-NN-agy.log`), `pages\`, `briefs\` (each brief as written), `evidence\` (saved output and other files a brief cites). |
| Panels about no feature | `<docs-root>\panels\<MM-DD>-<topic>\`, the one feature folder the tool makes itself. |
| Machine paths | Absolute paths are allowed (the worktrees folder; a rubric above the repo); relative paths resolve against the primary. |
| Old superpowers documents | Left where they are; nothing is migrated. |
| Levels | No user-level defaults file. Each project answers once. |

## Worked example

```toml
# .claude/parsec.toml  (primary checkout; .claude is gitignored here)
docs_root = "C:/Users/Brandon/Documents/KitnDev/_parsec/KitnUI"
worktrees = "C:/Users/Brandon/Documents/KitnDev/_worktrees"

[reviewer]                       # optional; these are the defaults
codex_lane          = "sol"      # or "astra"; round run's lane when --lane is omitted
backup_substitution = "ask"      # or "approved": Muse when codex is unavailable

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
