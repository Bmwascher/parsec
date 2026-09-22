# Driver rules

Six rules that cut across `design`, `build`, `debate` and `panel`. Each flow skill names this file in its first line.

1. **Background, named.** Every round, review, author run, build run, gate command and doctor run is dispatched in the background from the first attempt, named in Title Case for the person watching. A foreground call owns the session and hits the Bash tool's 10-minute ceiling. The names (this is their one home): `<Lane> R<n> <Kind> Round` for every CLI round and panel lane (`Astra R2 Design Round`, `Fable R1 Panel Round`); `Opus Pre-Review`; `Fable Last Look`; `Fable Poll`; `Author: <what>`; `Task 3 Implement`; `Gate: Busted`; `Pre-flight: Astra`; `Doctor`.
2. **The project's own rules outrank this plugin's sequence.**
3. **Open by reading** the feature's ledger and notes.
4. **Anything Brandon must read to decide** goes in chat or on a published page, never a sent Markdown file (it did not open on his phone, 2026-09-21).
5. **Never end a turn with a round unfinished** in an unattended run (2026-09-01: a run that did ended with no verdict).
6. **A statement a review refuted is corrected in place and dated**, and the whole defect class is swept, in whichever repo it sits.
