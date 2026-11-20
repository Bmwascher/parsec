# Gemini 4 Neon (`gemini-4-neon-high`)

The Neon lane, by name only from 2026-11-20 (Brandon: "Gemini by name"; "if I ask for google, it's neon first unless asked for Carbon like I would Astra"). Sol stays the default. agy runs it; the CLI facts and the read-only settings are in `agy-cli.md`.

## Dated facts

- Vendor guide: Google Cloud, "Developer's guide to Gemini 4 Neon", https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/guides/gemini-4-neon, read 2026-11-20. Thinking levels `LOW`, `MEDIUM`, `HIGH` (the default) and `XHIGH` ("supported for deep reasoning tasks"); `MEDIUM` "on latency-sensitive turns". One 1,048,576-token limit shared by input and output; output up to 65,536 tokens a segment. Code review is not named as a use case.
- Effort: `high`, Google's default, chosen by the id's suffix; the lane passes no `--effort`, though agy 1.5.13's help lists one (2026-11-20, saved as `11-20-gemini-reviewers/evidence/agy-help-1.5.13.txt` in the docs root). One timed reading run at `xhigh` (`gemini-4-neon-xhigh`, 2026-11-20): 752 s, `SUCCESS`, a VERDICT line last. Review quality at either level: UNMEASURED.
- Probes on agy 1.5.13 at `high` (2026-11-20): a full review of the probe tree, `VERDICT: FIX`, in 27 s; a real parsec package (the 0.1.52 Opus pre-review) reviewed in 203 s, `VERDICT: PASS` last, with the one Minor that Opus raised; the resume answered continuity in 29 s.
- A `GEMINI.md` or `AGENTS.md` in the reviewed tree reaches it as rules: a planted one put a word after the VERDICT line, which reads NONE (2026-11-20).
- A `hooks.json` in a tree's root `.agents/` folder, or in `.agent/`, `_agents/` or `_agent/`, the four names agy's skill `agy-customizations` lists, runs its hooks outside the deny rules (2026-11-20, `agy-cli.md`), so the tool refuses a Neon round on a head whose root tracks any of them in any letter case, as Windows ignores case; review such a head on another lane.
- Carbon: not listed for Brandon's Google login (2026-11-20); agy offers it only with an API key, Application Default Credentials or an enterprise gateway. Brandon: "C1 Neon only for now".
- Review quality against Sol: UNMEASURED.
