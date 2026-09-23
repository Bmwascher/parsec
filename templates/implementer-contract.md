# Implementer contract

Read by the `backup-implementer` alone; the Gemini lane gets the brief and nothing else. The brief is one task from a task list that a reviewed design produced. Your job is to build exactly that task.

## What to build

- Build exactly the task, transcribing its code. The fenced blocks are the code; you type them in, you do not improve them.
- The task's commit step is NOT yours: the session makes the commit after its own checks. Every other step is.
- The failing test first, and it must fail for the expected reason the task names. Then the implementation. Then the whole suite green, output clean, before you report.
- A task that says it has nothing worth testing under the project's test policy is built without a failing test, as the task says.
- No subagents.

## When the task is wrong

Say "this is too hard" or report the flaw. Never redesign, never substitute your own approach, never widen the task. A task whose code cannot work where it lands is reported as `blocked` with the evidence (the file, the line, the error).

## Report

Write the full report to the report path the dispatch names, with RED evidence (the failing run, the expected failure) and GREEN evidence (the passing run). Then reply in under 15 lines with one of five statuses:

- `done`: built, red seen, green seen, suite clean.
- `done with concerns`: built and green, with a named concern the session should read.
- `blocked`: the task cannot be built as written; the evidence says why.
- `needs context`: a file, rule or decision the brief did not give.
- `refused`: the CLI or model declined; quote its own message.

An empty diff is never `done`: a lane can decline the work and still exit 0, so the session reads the diff, not the status.
