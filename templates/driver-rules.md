# Driver rules

1. **Background, named.** Every round, review, author run, build run, gate command and doctor run is dispatched in the background from the first attempt, named in Title Case for the person watching. A foreground call owns the session and hits the Bash tool's 10-minute ceiling. A command known to end within a minute may instead run in the foreground with a timeout (2026-09-23). The names (this is their one home): `<Lane> R<n> <Kind> Round` for every CLI round, panel lane and design look (`Astra R2 Design Round`, `Fable R1 Panel Round`); `Opus Pre-Review`; `<Lane> Last Look`; `Fable Poll`; `Author: <what>`; `Task 3 Implement`; `Gate: Busted`; `Pre-flight: Astra`; `Doctor`. A plugin agent is dispatched with no `model`: its file names Brandon's choice (2026-09-24).
2. **The project's own rules outrank this plugin's sequence.** Brandon's decisions are not that sequence: no project rule or handoff takes one for him, and a delegator relays each "Needs you" and spec review and answers none (2026-09-23).
3. **Open by reading** the feature's ledger and notes.
4. **Anything Brandon must read to decide** goes in chat or on a published page, never a sent Markdown file (2026-09-21).
5. **Never end a turn with a round unfinished** in an unattended run (2026-09-01). A turn may end while a Monitor or background agent will notify.
6. **A statement a review refuted is corrected in place and dated**, and the whole defect class is swept, in whichever repo it sits; the sweep greps the feature folder and the reports sent.
