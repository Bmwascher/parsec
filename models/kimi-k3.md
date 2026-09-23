# Kimi K3 (`kimi-code/k3`, 1M context)

The backup review lane, on the Kimi CLI, read-only through `lanes/kimi-reviewer.md` (the agent file is the lane's only read-only control; its own name still says `parallax`, a stale wording accepted so the frozen copy keeps its hash).

## Effort

Set in the lane home's config as `default_effort = "high"` because the CLI has no effort flag; the pre-flight checks the key is there. The supported values are not in the measurements: UNVERIFIED.

## Measured here (2026-09-21)

- Round 1 with the agent file and an empty `--skills-dir`: exit 0, 28 to 46 s, the reply on standard output ending in a verdict line, the worktree clean outside the package.
- Round 2 with `--session`: exit 0, 9 s, recalled round 1 without re-reading; the read-only tool set persisted.
- `--skills-dir` at an empty folder suppressed the home's skills, with a positive control.
- A brief that said "in this directory" sent it looking beside the brief; it answered `VERDICT: FAIL`, which the tool reads as NONE.
- One Kimi round wrote `VERDICT: FIX`, a dash and a sentence; text after the word is allowed.

## Unmeasured

- Which bytes (CRLF or LF) the 2026-09-21 probes ran the agent file on.
- Continuity answers across three or more resumes.
- Behaviour on a diff-gate package larger than a few thousand lines.
