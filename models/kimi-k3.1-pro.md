# Kimi K3.1 Pro (`kimi-code/k3.1-pro`, 1M context assumed)

The review lane run by name, on the Kimi CLI, read-only through `lanes/kimi-reviewer.md` (the agent file is the lane's only read-only control; its own name still says `parallax` and the file is frozen).

## The switch from K3 (2026-10-23, Brandon)

- The lane ran K3 (`kimi-code/k3`) until 2026-10-23. Every measurement below was made on K3, not on K3.1 Pro.
- kimi 2.3.1's managed list (`kimi provider list`) offers K2.7 Coding, K2.7 Coding Highspeed, K3 and K3-256k only. The lane home holds a hand-written `kimi-code/k3.1-pro` alias (model `k3.1-pro`), copied from the K3 alias.
- One probe of each id, the same day: `k3.1-pro` answered; `k3.1`, `k3-1-pro`, `k3.1pro` and `k3-pro` were refused with `400 Your model id does not exist ... Please set model id as k3`.
- UNVERIFIED: the context size (the 1M in the alias is K3's), whether `default_effort` reaches the model, and a review round on K3.1 Pro.

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
