# Task list template

The task list (`tasks.md`) is what gets built. The `author` writes it to this file. A zero-judgment lane transcribes each task, so every task holds the FULL code, test and implementation, and decides nothing.

## Header

Before the tasks, in this order:

- **Goal**: one sentence.
- **Architecture**: the shape in a paragraph, naming the modules.
- **Tech stack**: languages, frameworks, test runner.
- **Spec**: the path of `spec.md`.
- **Global constraints**: a `## Global constraints` section holding every constraint from the spec and the project's rules that applies to more than one task, copied verbatim, never paraphrased. The tool slices this section into every task brief.

Then a `## File map`: every file the feature creates or changes, with one line on what each is for. A task names only files from the map.

## Task sizing

Small edits of one shape are one task (rename a field in five files: one task). A task is what one implementer can transcribe and one test run can check. A task never depends on a task after it.

## Task shape

Each task is a `## Task N: <name>` section holding:

- **Files**: the paths it creates or changes.
- **Consumes / produces**: what it needs from earlier tasks and what later tasks take from it.
- **Steps**, as checkbox items, in this order:
  1. Write the failing test, with the FULL test code in a fenced block, and the expected failure named.
  2. Run it and see the expected failure (red).
  3. Write the implementation, with the FULL code in a fenced block, complete, never a fragment or a placeholder.
  4. Run the tests and see them pass (green); the whole suite, output clean.
  5. Commit, as the LAST step, after a branch check, because phase chats share a checkout. The commit message is given in full.

The commit step belongs to the session. The test steps belong to the session on the Gemini lane (print mode runs no command) and to the `implementer` on its lane; they are written here so the record is complete.

## The three norms, written where they act

- **Red then green.** The failing test comes first and fails for the expected reason. A task that has nothing worth testing under the project's test policy says so in its steps and names its check instead.
- **YAGNI.** Only what the spec asks for. No option, hook or abstraction for a later feature.
- **DRY.** A second copy of a rule or a helper is a finding, not a convenience.

The project's test policy outranks the plugin's.

## No placeholders

Never: `TODO`, `...`, "add the rest", "similar to task 2", a fenced block that shows only the changed lines, a description of code in place of code, a step that says "verify it works". A fence holds a complete chunk that compiles on its own; a bare backticks-only line inside a fenced block is indented so it does not close the fence.

## Self-review, three points, before the file is handed over

- Every file in every task is in the file map, and every map entry is touched by a task.
- Every task's consumed items are produced by an earlier task.
- Every fenced block is complete, and the whole of the spec's behaviour section is covered by some task's test or named check.
