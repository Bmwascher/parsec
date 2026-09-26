# Ledger template

The head is written by hand once; the tool appends round lines, amendments and build lines, and never parses a line it did not write.

## Head

```
# <Readable title> (<year>)
topic: <topic>   branch: <branch>   base: <commit>
checkout: <path> (made by build | handed)
```

## Lines

`<time>` is `YYYY-MM-DD HH:MM ±hhmm`, from the tool or, by hand, the clock in the writing command (2026-09-23): bash `$(date '+%Y-%m-%d %H:%M %z')`, PowerShell `$((Get-Date -Format 'yyyy-MM-dd HH:mm zzz') -replace ':(?=\d\d$)')`. A hand-written line stays within 200 characters; a reason passed to the tool stays within 130, and the tool refuses a longer one. Longer detail goes in a file the line names.

A hand-written line never starts with a shape the tool writes: `<kind> r<n> <lane>:`, `amendment <k>:` or `build task <NN>` (field audit, 2026-09-23).

The hand-written shapes:

- The handoff facts: `- <time> handoff: <branch, base, finish rule, report destination>`.
- The go: `- <time> go: Brandon, "<his words>"` (or `pre-approved handoff`).
- The spec's approval: `- <time> spec approved: Brandon, "<his words>"`.
- A task result: `- <time> task 03: <commit>, <lane>, <tests: green | red: reason>[, whitespace trimmed]`.
- A decision on a finding: `- <time> decision <ID> (<kind> r<n> <lane>): <fix | ride | accepted as R<k> | change the approach>, Brandon, "<his words>"`; a ride on the reviewer's triage ends `<lane> triage` instead.
- A waiver: `- <time> waiver: <the look skipped, or the stand-in>, Brandon, "<his words>"`.
- An owed look: `- <time> owed: <the look or check>, <why>, <what clears it>`.
- A gate result: `- <time> gate <name>: <commit>, <green | red: reason>`.
- A smoke: `- <time> smoke: <commit>, <pass | fail: reason>, Brandon, "<his words>"`.
- The finish: `- <time> finish: <stop and report | merged <commit> | PR <url>>`.
