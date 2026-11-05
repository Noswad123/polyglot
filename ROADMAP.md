# Polyglot: practice-first roadmap

## Direction

Keep the Rustlings-style learning loop; stop making a learning platform a
prerequisite for using it:

**Choose a small exercise → attempt it → run a check → understand the feedback →
try again.**

Success means being able to open this repository and start practicing within two
minutes after initial language setup. This is a personal practice space, not a
promise to build a complete curriculum for every language.

## Ownership boundaries

| Space | Authoritative content |
|---|---|
| Darkness (`~/projects/darkness`) | Concept explanations, mental models, language comparisons, resources, learning takeaways, and personal learning priorities |
| Polyglot | Exercise prompts, starters, tests, runnable examples, implementations, and run instructions |
| Optional Polyglot tooling | Features that make an already-useful practice loop easier |

- Keep general software notes in Darkness. Do not migrate them back here.
- Short illustrative snippets in notes are fine; avoid maintaining complete
  runnable solutions in both places.
- Exercise-specific instructions belong beside the exercise.
- Link to an existing note when it helps. Links must not become a database or
  synchronization dependency.
- Note completeness, a passing exercise, and lasting fluency are different things.
  Do not collapse them into one mastery status.

## Working constraints

- One primary learning language per short learning cycle. A familiar reference
  language is optional.
- No requirement to implement every concept in every language.
- Keep one next action visible; resource catalogs and exercise ideas are not
  today's assignments.
- Include practical tasks as well as algorithms: text processing, files, errors,
  collections, tests, and small refactorings.
- Preserve existing code and ideas. Reorganize only when it removes friction from
  an actual practice session.
- Keep personal learning priorities in Darkness; this roadmap tracks repository
  improvements rather than a second personal progress system.

## Phase 1 — Make the repository usable without the platform

**Scope:** a clear front door and one tiny, repeatable practice track.

- [x] Make the root README practice-first and document the notes boundary.
- [x] Preserve the earlier philosophy and platform proposals separately.
- [x] Provide three small Python exercises with explicit contracts and checks.
- [x] Keep blank starters separate from local answers and existing solutions.
- [x] Document setup, checking one exercise, checking the track, and retrying.
- [x] Verify that blank starters fail for the intended reason and valid answers
      pass, without the CLI, database, or third-party packages.

Python is a provisional starting point because it has the most developed existing
practice material. It is not a decision about the user's primary learning language.
Hello World is a setup check, not an assessment of programming ability.

**Acceptance:** from the root, follow the documented commands, edit a local answer,
and receive feedback. Existing reference implementations remain unchanged. No
database, API, UI, or progress service is needed.

**Validation completed:** blank starters raised the intended `NotImplementedError`;
temporary valid answers passed all three exercise checks (including 12 search
cases and nine last-word cases). Whole-track checks passed on Python 3.12.11 and
3.15.0; each individual exercise command passed on 3.15.0. Local answers were then
restored to blank starters. Focused existing kata checks also passed: 10 passed,
one expected failure. This was not a full-repository test run.

## Phase 2 — Use the loop before expanding it

**Scope:** a few real sessions, not another infrastructure sprint.

- [ ] Choose the primary language and a concrete capability to improve.
- [ ] Add a small Current Practice section to an existing programming hub in
      Darkness, when ready; do not create another dashboard.
- [ ] Complete a few sessions and retry an exercise without consulting its solution.
- [ ] Record only useful discoveries or misconceptions in existing concept notes.
- [ ] Identify actual friction before deciding the next repository change.

Suggested Current Practice section:

```markdown
## Current Practice

- Focus: one capability in one language
- Reference: link to an existing concept note
- Exercise: path or link to runnable practice
- Next action: one concrete step
```

**Acceptance:** choosing and starting practice feels straightforward. If the
starter track is too basic, replace or skip it; completing a prescribed curriculum
is not the goal.

## Phase 3 — Add one useful learning slice

**Start only after:** the primary language and next capability are chosen.

- [ ] Add or adapt one exercise relevant to that capability.
- [ ] Give it a prompt, starter, check command, and explicit success conditions.
- [ ] Link a relevant Darkness note where useful; do not duplicate its explanation.
- [ ] If comparison helps, implement the same contract in one reference language.
- [ ] Use native language tools directly before considering a common runner.

**Acceptance:** the new exercise supports a real learning goal and can be checked
independently. Another language does not require filling a language-by-concept
matrix.

## Phase 4 — Maintain only what practice demonstrates is useful

This is a decision gate, not a commitment to build more software.

Possible changes, only in response to repeated friction:

- A shortcut for a frequently typed check command.
- A small exercise index if navigation becomes difficult.
- Fixing a note-to-code link when that note is used.
- A watcher or lightweight runner if manual checks are genuinely disruptive.

**Acceptance:** each tooling change removes an observed obstacle and keeps direct
exercise commands usable without it.

## Deferred, not required

- Database-backed mastery and automated next-exercise selection.
- Notes ingestion, synchronization, shared schemas, and CQRS integration.
- New frontend/backend work for the learning platform.
- A CLI per language or a universal exercise runner.
- Bulk note cleanup, wholesale directory migration, and complete language parity.

The [earlier vision](README/vision.md) and existing code remain available. Building
the platform can be an intentional software project later, separate from a
programming-practice session.

## Current next action

Phase 1 is complete. Choose the primary learning language and one capability for
Phase 2 before expanding the exercise catalog. The Python starter track is
available immediately as a setup check, not a required learning assignment.
