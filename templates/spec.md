# Spec template

The spec is the design document of one feature: what it does and why, which Brandon reviews before the task list is written. No code in it; the code lives in the task list.

The spec opens with an unnumbered `## Decision summary`, before section 1: at most 150 plain words on what the feature changes and what Brandon is asked to approve. The driver posts it in chat (`brainstorm`). It names each follow-up the design creates as an open question, and after approval states the decisions (2026-09-24).

## Sections, in this order

1. **Goal.** One paragraph: what the feature does for the user, and what it deliberately does not do.
2. **Context.** The handoff or notes it comes from, the branch, the base, and the checkout. Names given by a handoff are recorded as given.
3. **Approach.** The chosen approach and the two or three that were rejected, each with the reason, in Brandon's own words where he gave them.
4. **Design.** The files, names, signatures and call sites touched, with the patterns already in the code that they follow. Design for isolation; no unrelated refactoring.
5. **Behaviour.** The observable behaviour, case by case, including errors and edges.
6. **Testing.** What the project's test policy calls for here, and any case that has nothing worth testing, named with its check instead.
7. **Open questions.** Anything still to decide, each with its owner; never a question the notes already answer. With none, the section says "Open questions: None."

Goal and Behaviour state the current design, with no round tag or date; a correction's source goes in Approach or the ledger.

## Self-review, four points, before the file is handed over

- Every behaviour in section 5 traces to a sentence in section 1.
- Every file in section 4 exists, or its creation is stated.
- No sentence promises what section 6 does not test or check.
- Nothing here restates a project rule; it points to the rule instead.
