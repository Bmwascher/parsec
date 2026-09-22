# Ledger template

`ledger.md` sits loose in the feature folder. The head is written by hand once; the tool appends round lines, amendments and build lines, and never parses a line it did not write.

## Head

```
# <Readable title> (<year>)
topic: <topic>   branch: <branch>   base: <commit>
checkout: <path> (made by build | handed)
```

"made by build" or "handed" decides what `build` may remove.

## The four hand-written line shapes

- The go: `- <time> go: Brandon, "<his words>"` (or `pre-approved handoff`).
- A task result: `- <time> task 03: <commit>, <lane>, <tests: green | red: reason>`.
- The handoff facts: `- <time> handoff: <branch, base, finish rule, report destination>`.
- The finish: `- <time> finish: <stop and report | merged <commit> | PR <url>>`.
