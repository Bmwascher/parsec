# Working on parsec

Gotchas for this repo only. The design, with every dated failure behind every rule, lives in Brandon's rethink notes; the plugin's own rules are in its skills.

- **The version bump is the LAST commit before the Fable last look**, so the last look reviews the bumped head and the final PASS names it. The plugin cache is keyed on the version string in `.claude-plugin/plugin.json` and served a stale install three times (old item 65). After the merge: refresh the marketplace, then update, then check the installed commit against the repo head (`/doctor` shows it).
- **`CHANGELOG.md`** holds one `## vX.Y.Z (date)` section per version, newest first, the newest equal to `plugin.json`; `evals/tools/check_changelog.py` runs it through the STE checker, and CI runs both on every push.
- **The family git guard** denies a commit message that merely names a flag such as `-a` (old item 79). Stage by explicit path.
- **Skills name the tool by `${CLAUDE_PLUGIN_ROOT}/tools/parsec.py`**, never a bare path and never by searching (old item 58: the oldest of ten cached copies ran).
- **Budgets are tests.** `evals/tests/test_budget.py` counts the tool (1,000 lines), the tests (1,500), the frozen checkers (522) and the prose (10,000 words, 1,600 per skill). An addition that would pass a budget deletes something first.
- **Frozen copies.** The two checkers, their allow list, their two tests, `lanes/kimi-reviewer.md` and `LICENSE` are byte-for-byte copies from the old repo; their blob ids are in the rethink's step 5. Do not tidy them.
- **The refuted-sentence rule** is rule 6 of `templates/driver-rules.md`.
- Python 3.12 and PowerShell 7 only.
