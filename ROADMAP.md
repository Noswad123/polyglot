# Polyglot: practice-first roadmap

## Direction

Keep the Rustlings-style learning loop; stop making a learning platform a
prerequisite for using it:

**Choose a small exercise → attempt it → run a check → understand the feedback →
try again.**

Success means being able to open this repository and start practicing within two
minutes after initial language setup. This is a personal practice space, not a
promise to build a complete curriculum for every language.

## Agreed end state

**Darkness is the knowledge store. Polyglot is the executable practice system.
One Rust-based Polyglot CLI is its front door, with a shared Rustlings-inspired
workflow and native language adapters. A web UI is optional.**

These are responsibilities, not three independently deployed products. Start with
files and native language tools, not a shared database or required backend service.
The CLI connects practice to references without duplicating knowledge or
automatically rewriting notes. See the [target architecture](README/architecture.md)
for the current implementation and integration rules.

The direction is accepted in
[ADR 0001](README/decisions/0001-shared-workflow-language-adapters.md).
The Python CLI is a working prototype, not the final implementation language.
The Rust list/start/check workflow and two native adapters are implemented and
validated. The first shared line-based prompt/hint/navigation session is also
implemented; watch/resume and adoption remain future gates.
The initial Python-only milestones below remain completed historical work; later
gates supersede the earlier sequencing without discarding the prototype.

## Ownership boundaries

| Space | Authoritative content |
|---|---|
| Darkness (`~/projects/darkness`) | Concept explanations, mental models, language comparisons, resources, learning takeaways, and personal learning priorities |
| Polyglot | Exercise prompts, starters, tests, runnable examples, implementations, and run instructions |
| Polyglot CLI | Finding exercises, safely preparing attempts, and invoking native checks |
| Optional services and UI | Later interfaces or storage, only if practice demonstrates a need |

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

## Phase 1b — Establish the single CLI entry point

**Scope:** a thin interface over the existing track, following agreement on the
long-term architecture. This does not expand the curriculum or select the primary
learning language.

- [x] Document Darkness, Polyglot, and the CLI as complementary responsibilities.
- [x] List the existing exercises without loading notes or writing files.
- [x] Prepare a shared local answer file without overwriting an existing attempt.
- [x] Check one exercise or the whole track through native unittest commands.
- [x] Validate preservation, failure reporting, and use outside the repository cwd
      with isolated integration tests.
- [x] Document the CLI while retaining direct native commands as an alternative.

**Acceptance:** one dependency-free entry point supports list → start → check.
Invalid selections do not write files, failed checks remain failures, and existing
answers are preserved. No database, note sync, backend service, or plugin framework
is introduced.

**Validation completed:** 11 isolated CLI integration tests passed on Python
3.12.11 and 3.15.0. They cover listing/help without writes, invalid selections,
preserving existing answers, rejecting symlink/directory answer paths, missing
files, intended starter failures, individual and whole-track success, syntax
errors, import side effects, unrelated working directories, and paths with spaces.
Tests use disposable fixtures and do not touch local practice answers. Python 3.11
compatibility was reviewed, but execution was validated on 3.12 and 3.15 only.

## Phase 2 — Prove a shared Rust workflow with two adapters

**Scope:** a small Rust list/start/check slice, not a full Rustlings fork or TUI.
Implemented and validated; see the [Rust proof instructions](README/rust-cli.md).

- [x] Record the shared workflow, exercise model, and adapter decision in an ADR.
- [x] Introduce a small Rust CLI with one orchestration path and built-in Python
      and Rust adapters; no plugin framework.
- [x] Describe exercise identity separately from workspace identity and native
      check selection. Expose the existing Python exercises without moving them.
- [x] Add one isolated Rust starter/check pair, independent of older Rust projects.
- [x] Preserve current attempt files and the prototype's safe start/check behavior.
- [x] Define Python interpreter selection and version validation for a Rust host.
- [x] Distinguish known blocked checks from learner failures, keeping native
      diagnostics and an indeterminate outcome where classification is uncertain.
- [x] Record the reuse choice: no upstream code copied for this slice. Pin and
      attribute any future code reuse.

**Proof gate — all must pass before interactive features:**

- [x] Both languages use the same workflow; only the adapter constructs native
      invocations. Rust checks do not build unrelated projects.
- [x] Blank attempts fail intentionally, valid attempts pass, and individual Python
      checks work while other exercises remain unfinished. Zero selected tests
      cannot count as success.
- [x] Missing tools and invalid check targets are reported distinctly from known
      learner errors. Listing does not require every language tool to be installed.
- [x] Repeated/concurrent starts preserve source files; invalid selections and
      checks of missing attempts do not create or reset them.
- [x] Commands work from unrelated directories and paths with spaces, using
      explicit working directories and argument vectors, not shell interpolation.
- [x] Native checks remain independently usable and agree with CLI outcomes.
- [x] Tests use isolated workspaces, not real learner attempts or Darkness.

No watcher, progress store, automatic reset, dependency installer, or UI is needed
to pass this gate. Keep the current Python CLI available throughout.

**Validation completed:** Rust/Cargo 1.89.0 on macOS; format, three Rust unit tests,
Clippy with warnings denied, and locked offline build all passed. The 26 isolated
integration tests passed with Python 3.12.11 and 3.15.0. They include native-check
parity, concurrent preserving starts, tool/harness failures, zero/ignored tests,
fresh-source checks despite stale bytecode, nested build-directory symlinks, and
missing/stale lockfiles. All 11 Python-prototype regression tests also passed.
Rust 1.85 is the declared build minimum, not an executed test matrix entry.

Current boundaries: one workspace mapping per language; native output is buffered
until each process finishes; Rust classification uses Cargo JSON and libtest text.
That validation covered the non-interactive proof, not a full-repository test run.

## Phase 3 — Add the Rustlings-style interaction

**Start only after:** the two-language proof gate passes.

- [x] Add prompt/hint presentation and next/previous selection through shared
      session policy; adapters do not control navigation.
- [x] Demonstrate select → edit → check → hint → next in both languages.
- [ ] Add watching as a separate increment, accounting for shared answer files and
      relevant test/config inputs rather than assuming one file per exercise.
- [ ] Cancel or supersede old runs safely; do not display stale success after an
      edit or a change of selected exercise.
- [x] Keep explicit check commands available outside interactive mode.

**First increment validated:** `practice [python|rust|ID]` provides an in-memory,
line-based session; `show ID` and `hint ID` are read-only. `next` reruns the current
check and advances only on success. Normal checks do not advance; quit/EOF ends
the session without claiming completion. Navigation prepares before committing
selection, preserving shared answers across exercises and languages.

All 20 isolated interaction tests and all 26 adapter regressions passed with
Python 3.12.11 and 3.15.0 on macOS. Three Rust unit tests, format, Clippy with
warnings denied, locked offline build, and all 11 prototype regressions passed.
Coverage includes a live external edit after a pass, blocked-check recovery,
boundaries, failed destination preparation, menus, hints, and preservation.

**Still open:** watching and stale in-flight result handling. The session does
not observe edits while a check is running; save edits before requesting a check.
This phase is partially complete, not the full save-triggered Rustlings flow.

**Acceptance:** the same user flow works across both languages, preserves raw
native feedback, and remains usable when note references are unavailable.

## Phase 4 — Add minimal local resume behavior

**Start only after:** interaction and check invalidation behavior are established.

- [ ] Store the selected language/exercise and minimal completion history locally.
- [ ] Define how changed sources or check definitions invalidate current results.
- [ ] Handle missing or damaged state without overwriting practice files.
- [ ] Verify restart/resume behavior and interrupted checks in both languages.

**Acceptance:** resuming is convenient, but stored progress is neither proof of
current correctness nor a mastery score. No database or notes synchronization is
required; adapters do not write session state.

## Phase 5 — Adopt the Rust CLI before retiring the prototype

**Start only after:** the prior gates pass and real sessions confirm the workflow.

- [ ] Compare the Rust entry point against the prototype's selection, preservation,
      working-directory, and failure-reporting behavior.
- [ ] Use both Python and Rust exercises in real practice sessions.
- [ ] Document build/run requirements and switch the README's primary commands
      only after the replacement is validated.
- [ ] Propose wrapping or retiring `polyglot.py` separately. Do not delete it,
      existing `pylearn` code, or learner attempts as an incidental migration.

**Acceptance:** the replacement is useful in practice, not merely compilable.
Installation/distribution can be added without making a web service necessary.

## Practice and curriculum discipline throughout

These remain learning choices, not prerequisites for the two-language technical
proof. Two adapters do not imply two mandatory learning tracks.

- Choose one primary learning language and a concrete capability to improve.
- Keep a small Current Practice section in an existing programming hub in Darkness:
  focus, concept-note reference, exercise link, and one next action.
- Complete a few sessions and retry without consulting the solution. Record only
  useful discoveries or misconceptions in existing notes.
- Add the next useful exercise after identifying a learning need, not to fill a
  language-by-concept matrix. Give it a prompt, starter, and native success check.
- Link or repair relevant note references as they are used; avoid bulk migration.

## Deferred, not required

- Database-backed mastery and automated next-exercise selection.
- Notes ingestion, synchronization, shared schemas, and CQRS integration.
- New frontend/backend work for the learning platform.
- A CLI per language, dynamic plugins, or a generalized framework that replaces
  native tools. The shared Rust workflow and two built-in adapters are in scope.
- A full Rustlings fork by default, automatic environment setup, or a broad rewrite
  of existing exercises before the two-language proof.
- Bulk note cleanup, wholesale directory migration, and complete language parity.

The [earlier vision](README/vision.md) and existing code remain available. Building
the platform can be an intentional software project later, separate from a
programming-practice session.

## Current next action

Phases 1, 1b, and the Phase 2 proof gate are complete; Phase 3 prompt/hint/navigation
is validated. Try `practice` without retiring the Python prototype. The next code
change is the separate watch increment, including shared-file/config invalidation
and superseded-run handling. Do not introduce persisted progress or retire the
prototype before their later gates pass.
