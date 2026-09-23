---
name: panel
description: Use when Brandon asks for a panel (several lanes answer one question blind) or a poll (one Fable second opinion in chat); `/panel` works too. Never triggered on the plugin's own initiative.
---

# panel

Rules that cut across the flow are in `${CLAUDE_PLUGIN_ROOT}/templates/driver-rules.md`; read it first. The rounds run as in `debate`, "Running a round", with `--kind panel`.

- **At least one cross-vendor lane** (Sol, Astra by name, or Kimi); never an all-Claude panel. Most panels are two lanes.
- **Hub and spoke**: lanes never talk to each other or learn who raised a point.
- **The brief** follows `templates/brief-panel.md`, which holds what the host must give and the order the lanes answer in. One brief file serves every lane: `round run` for Astra or Sol and for Kimi, `round prepare` plus `reviewer-fable` plus `round collect` for Fable, each its own named background task (`Astra R1 Panel Round`, `Fable R1 Panel Round`).
- **The host checks each claim** against the repo before relaying it and marks what it could not check UNVERIFIED. A point raised by more than one lane is the strongest signal, counted once and marked convergent. A split between lanes is a signal to read the file, never a tie the host breaks by preference (old item 74).
- **One round.** A follow-up to a lane that already answered is the next round with that lane alone, so it keeps its context. A second, unrelated panel in the same feature takes each lane's next number and `--fresh`. `round close --feature <folder> --kind panel` runs after the host has reported.
- **The host reports** the lanes side by side, names any new option, and says plainly whether its own recommendation changed. Brandon may ask for a blind panel; the host then leaves its recommendation out.
- **Where it lives.** In the open feature folder, or, about no feature, under `<docs-root>\panels\<MM-DD>-<topic>\`, which the tool makes. Panel round folders are not committed while the panel is open (`setup`, "Tracked docs root").
- **A lost lane** stops and asks Brandon, never quietly a smaller panel.
- **Poll.** "Poll Fable" from an Opus session is not a round: dispatch `reviewer-fable` (`Fable Poll`) with the same kind of brief (a file in the open feature folder, or a loose file under `panels\` when there is none) and no report path, and post its answer in chat. A same-vendor second opinion, never a gate, recorded only when Brandon asks.
