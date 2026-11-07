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
The root Python prototype is retired; the supported practice CLI is Rust-based.
The Rust list/start/check workflow and two native adapters are implemented and
validated. The first shared line-based prompt/hint/navigation session is also
implemented. Explicit checks are the intended interaction; watch mode and
save-triggered checking are out of scope by user choice. Resume is optional,
not a prerequisite for using the app.
The initial Python-only milestones below remain historical work. Their recorded
validation does not imply that the retired prototype is still supported.

The Git ownership decision is recorded in
[ADR 0002](README/decisions/0002-pristine-main-practice-branches.md): main is
canonical and learner work belongs on another branch. This reprioritizes tracked
per-exercise files and reset. The Rust CLI now uses independent
tracked exercise modules and explicit reset; legacy shared answer files are
retained untouched, not automatically imported. Canonical baseline commits still
require user review and integration into main.

Discovery now covers the complete current-file inventory: 37 topic families,
20 question documents, and 70 solution artifacts in the user-selected
language directories under `practice/`.
The artifacts include the original 60 legacy files and ten examples checked
against the current native tests, not a proof of all behavior.
The JSON `references` field is retained for export compatibility. Question readiness
and native practice availability are separate: only five contracts are curated
and all five have Python and Rust bindings (ten runnable exercises). Earlier
five-question milestones describe that
curated subset, not the size of the original collection.

## Ownership boundaries

| Space | Authoritative content |
|---|---|
| Darkness (`~/projects/darkness`) | Concept explanations, mental models, language comparisons, resources, learning takeaways, and personal learning priorities |
| Polyglot | Exercise modules, prompts, tests, runnable examples, implementations, and run instructions |
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
to pass this gate. The Python CLI was retained during that proof and is now retired.

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

## Phase 3 — Rustlings-style interaction with explicit checks

**Start only after:** the two-language proof gate passes.

- [x] Add prompt/hint presentation and next/previous selection through shared
      session policy; adapters do not control navigation.
- [x] Demonstrate select → edit → check → hint → next in both languages.
- [x] Keep checking deliberate: Enter/`check`/`c` checks the selected exercise;
      `next` rechecks before advancing. No checking on save or automatic advancement.
- [x] Keep explicit check commands available outside interactive mode.

**First increment validated:** `practice [python|rust|ID]` provides an in-memory,
line-based session; `show ID` and `hint ID` are read-only. `next` reruns the current
check and advances only on success. Normal checks do not advance; quit/EOF ends
the session without claiming completion. Navigation prepares before committing
selection, preserving shared answers across exercises and languages.

At this milestone, all 20 isolated interaction tests and all 26 adapter regressions passed with
Python 3.12.11 and 3.15.0 on macOS. Three Rust unit tests, format, Clippy with
warnings denied, locked offline build, and all 11 prototype regressions passed.
Coverage includes a live external edit after a pass, blocked-check recovery,
boundaries, failed destination preparation, menus, hints, and preservation.

**Accepted interaction:** the user explicitly chose manual checks, not watch mode.
This interaction phase is complete for that scope. Save edits before requesting a
check or reset and wait for it to finish before editing again. There is no pending
save-triggered or background-checking increment.

**Acceptance:** the same user flow works across both languages, preserves raw
native feedback, and remains usable when note references are unavailable.

## Branch safety and independent exercise layout

The learner-facing layout decision supersedes the shared-answer-file prototype.
Deliver Git safety first, then migrate the files without losing attempts.

- [x] Record main as the canonical blank baseline and practice on non-main branches.
- [x] Automatically create a unique practice branch from clean main; preserve
      existing non-main branches and refuse dirty-main/detached/unborn contexts.
- [x] Guard direct start and revalidate session checks/navigation after external
      branch changes. Keep standalone inspection/checks usable on main.
- [x] Add an explicit opt-in staged-exercise commit guard without overwriting
      existing hooks or changing Git configuration.
- [x] Implement independent modules under `practice/<language>/exercises/` and
      selected test imports; remove the active starters/answers split.
- [x] Preserve existing shared answer implementations untouched, keeping them out
      of the pristine baseline; document explicit manual copying without guessing
      at shared imports/helpers or deleting the original files.
- [x] Specify reset against a pinned regular-file blob from strict local
      `refs/heads/main`, with object replacements disabled, confirmation, private
      snapshot backup and lasting original-inode recovery, and no index changes.
- [x] Validate blank main versus edited practice branches and reset behavior in
      isolated committed fixtures, including late saves and staged content.
- [x] Confirm that the four original canonical blank modules are committed in local main;
      no additional baseline commit is needed for these existing exercises.
- [ ] Try the updated layout/reset in a personal practice session. New authored
      exercises still need reviewed integration into main before reset can use them.

**Scope limit:** CLI guards apply to the shared Rust entry point. Editors and
direct native tools do not gain filesystem protection; local hooks are
optional and bypassable. Remote main-branch rules are owner-managed separately.
The initial branch-safety increment did not migrate layout or add reset. The next
increment now implements both while preserving the legacy files. `start` only
validates existing tracked files. Unsupported reset platforms/filesystem primitives
block rather than using an unsafe overwrite fallback; macOS is runtime-tested,
Linux is implemented but not yet runtime-tested.

**Validation:** 100 isolated Python 3.15 integration/regression tests passed,
including 22 branch-policy, 15 hook, and four hostile-Git-context fixture-isolation
tests. Three Rust unit tests, format, Clippy with warnings denied, and locked
offline build passed. No branches, hooks, configuration, index entries, or commits
were changed in the real checkout by those tests; fixture commits use temporary
repositories and isolated Git configuration.
The 22 branch, 15 hook, and four isolation tests also passed with Python 3.12.11.

**Independent-file/reset validation:** 130 integration/regression tests passed
on Python 3.15, including 29 reset cases; those reset cases also passed on Python
3.12.11. Eleven Rust unit tests passed on Rust 1.85 and 1.89. Deterministic native
tests cover conditional installation, late editor writes through held descriptors,
retained recovery inodes, directory redirects, and private permissions. Format,
Clippy with warnings denied, and locked offline build passed. Legacy attempts in
this checkout were not modified. Platform runtime coverage is macOS; Linux reset
runtime validation remains open. The new blanks are not committed automatically.

## Phase 4 — Optional minimal local resume behavior

**Start only if:** repeated practice shows that remembering the selected exercise
is useful. This is not required for the explicit-check workflow or prototype retirement.

- [ ] Store the selected language/exercise and minimal completion history locally.
- [ ] Define how changed sources or check definitions invalidate current results.
- [ ] Handle missing or damaged state without overwriting practice files.
- [ ] Verify restart/resume behavior and interrupted checks in both languages.

**Acceptance:** resuming is convenient, but stored progress is neither proof of
current correctness nor a mastery score. No database or notes synchronization is
required; adapters do not write session state.

## Phase 5 — Consolidate the supported Rust CLI

Prototype retirement was explicitly approved independently of optional resume.
The shared Rust CLI is now the sole supported practice entry point.

- [x] Re-run selection, preservation, working-directory, failure-reporting, and
      reset regressions after removing the unused prototype.
- [ ] Use both Python and Rust exercises in real practice sessions.
- [x] Document build/run requirements and recommend the validated, branch-guarded
      Rust entry point in the README. This safety-driven documentation switch does
      not imply every language track has been used in a real session.
- [x] Retire the root Python prototype, its prototype-only tests, aggregate legacy
      harness, and unused starter files. Preserve learner answers if present and
      leave the unrelated packaged `src/python/pylearn` experiment untouched.

**Acceptance:** the replacement is useful in practice, not merely compilable.
Installation/distribution can be added without making a web service necessary.

**Cleanup validation:** 119 active integration/regression tests passed after
removing the 11 obsolete root-prototype tests. All 11 Rust unit tests, format,
Clippy with warnings denied, locked offline build, and diff checks passed. Active
exercise files and learner answers were not deleted; the four canonical blank
files were confirmed in committed local main. These counts supersede earlier
prototype-inclusive totals for the current suite.

## Shared question library and kata conversion

Keep the existing `README/katas/` documents as the shared question library rather
than duplicating each question across language tracks. A `Problem` owns its stable
ID, title, and Markdown path; each native `Exercise` references it and adds the
language API, blank file, hint, and test selector. General notes remain in Darkness.

- [x] Curate five contracts: Hello World, Find in String, Length of Last Word,
      Binary Search, and Fibonacci. Make edge cases and binding differences explicit.
- [x] Add `questions` and `question PROBLEM_ID`; show shared Markdown plus a native
      task in `show` and the session. Read current docs without rebuilding. Full
      inventory discovery below supersedes the original curated-only listing.
- [x] Keep checks independent of question availability; validate question display
      before branch creation or selection changes, without revealing native hints.
- [x] Convert Python Binary Search and Fibonacci into blank modules with native
      checks. Fibonacci covers every core length `0..40`; Binary Search checks
      sorted presence, strict booleans, edge cases, and input preservation.
- [x] Preserve the original kata implementations and four active exercise bodies.
      Implementations were subsequently relocated byte-identically to `solutions/`;
      they are never copied into canonical blanks or marked verified by location.
- [x] Publish a readiness table and 15-document remaining conversion queue, including
      contradictory or incomplete contracts, without implying all languages are ready.
- [x] Confirm the two converted Python modules reached committed main; all six
      pre-batch exercises have canonical reset baselines.
- [ ] Choose the next question or language binding from the library based on a
      learning need, resolving its contract before adding a native check.

**Validation:** 135 isolated integration/regression tests passed with Python 3.15;
all 15 question-library tests also passed on Python 3.12. Twelve Rust unit tests
passed on Rust 1.85 and 1.89, along with format, Clippy with warnings denied,
and locked offline build. Coverage includes runtime question edits, shared/native
bindings, missing/empty/symlink question handling, selection retention, native
contract failures, reset of the new exercise files, and regression safety.

At this initial conversion milestone, five Python bindings and only `rust/hello`
were available. The paired-track batch below now completes both languages.
Drafts and reference-only topics are now discoverable through the full inventory
below, but no unsupported language or completed reference is implicitly converted
to a native binding. See the [question library](README/katas/index.md) for scope.

## Full original-collection discovery

The app must not hide the original collection behind a small converted subset.
Keep discovery metadata independent from executable exercise bindings.

- [x] Register all 37 normalized topic families: five curated contracts, 15 draft
      documents, and 17 code-only topics needing shared questions.
- [x] Preserve all 20 question-document paths and map all 60 current legacy source
      artifacts across eight languages, excluding tests, manifests, generated
      outputs, playgrounds, and idea-only backlog entries.
- [x] Make `questions` expose the full inventory. JSON is now the default for
      exports/integrations; explicit `--json` remains a compatibility alias.
- [x] Replace the original tab-separated human output with `questions --pretty`:
      an aligned ASCII table fitting 80 columns, wrapped reference languages,
      runnable practice languages, and a legend/details command. Exact binding
      IDs, titles, and reference paths remain in JSON and `question ID`.
- [x] Keep JSON output free of table headers and summaries; reject mixed or repeated
      format flags rather than guessing which mode was intended.
- [x] Let `question ID` inspect drafts and missing-question topics without inventing
      a contract. Show empty drafts explicitly and label reference paths unverified.
- [x] Keep `list` and all practice/check/reset selection restricted to the existing
      six bindings. Discoverability must not create stubs or enable more adapters.
- [x] Independently audit every question document and source artifact against the
      repository tree, so future inventory additions cannot silently disappear.

These are source artifacts, not 60 verified solutions or 37 fully specified
exercises. Multiple functions/variants in a file remain grouped by topic pending
contract review. The empty Python pivot-index artifact is explicitly a placeholder;
the empty Sudoku document is draft, not an absent question. Historical Git-only
assets are outside this current-file inventory; no references are executed or moved.

**Validation:** 140 isolated CLI integration/regression tests passed with Python
3.15. The independent document/source inventory audit also passed with Python 3.12.
Twelve Rust unit tests passed on Rust 1.85 and 1.89, plus format, Clippy with
warnings denied, and locked offline build. Coverage audits the actual source/doc
tree, topic normalization, statuses, strict JSON, read-only detail views, unsafe
documents, and rejection of inventory-only topics as native exercises. The legacy
implementation/test suites themselves were not executed or certified by this audit.

**Output-format validation:** default JSON and explicit `--json` were verified
equivalent, with the same schema and no human output mixed in. `--pretty` retains
all 37 IDs and every reference/practice language across wrapped rows, uses no tabs
or ANSI escapes, and stays below 80 columns. Mixed/repeated flags are rejected.
All 140 CLI regression tests and 14 Rust unit tests passed; Rust units passed on
1.85 and 1.89, alongside format, Clippy, and locked offline build checks.

## Historical solutions tree organization

This records the earlier root-tree migration. The user subsequently selected the
current `practice/` layout and removed legacy tooling/tests; this historical
record is not a requirement to restore those directories or absent assets.

The learner-facing distinction at that milestone was shared questions, editable exercises, and
stored solution attempts. `solutions/<language>/` replaces the former implementation
kata directories; the question documents remain under `README/katas/`.

- [x] Relocate all eight implementation trees and the seven external Python tests,
      preserving Users project nesting, manifests, locks, package context, and both
      SQLite databases. The 94 original tracked files retain identical bytes and
      executable modes; ignored caches moved with their parent trees, not deleted.
- [x] Point all 60 catalog artifacts at `solutions/<language>/...` without changing
      the 37 topics, question statuses, or six native practice bindings.
- [x] Rename the pretty column, details heading, and footer to Solutions. Keep the
      existing JSON `references` key and entry schema for export compatibility;
      its paths now identify solution artifacts. The folder is not certification.
- [x] Preserve legacy Python test bytes via a narrowly scoped `katas` compatibility
      package. Keep submitted code ahead of stored solutions and avoid putting bare
      `solutions/python` on the import path where `queue.py` could shadow stdlib.
- [x] Update legacy test/configuration paths and remove obsolete package-data globs.
      Disable the old question-README generator rather than overwrite curated
      contracts. Native practice remains independent of the legacy experiment.
- [x] Retain TypeScript specs and server/database projects without claiming their
      old harnesses or runtime dependencies are repaired by relocation.
- Superseded: the former root `solutions/` tree and Python compatibility package
  are not the current layout and must not be recreated to satisfy this record.

The scoped legacy Python tests passed (25 passed, one expected failure). That is
not proof that every stored solution conforms to the current shared contract.
Servers were not launched and databases were not regenerated by migration.

**Migration validation:** all 145 root integration/regression tests passed with
the repository's Python 3.12 development environment, including the optional
pytest-backed legacy-runner compatibility check. All 14 Rust units passed on
Rust 1.85 and 1.89; format, Clippy with warnings denied, locked offline build,
and diff checks passed. The 94 byte/mode-preserving relocations were re-audited
against pre-move commit `6412bed` after tests, including both SQLite databases.
The user-created `remove old katas` commit was not amended or undone. Current
user-selected paths, rather than the obsolete root tree, belong in subsequent
reviewed commits.

## User-selected layout and link cleanup

Preserve the current directories, including their spelling, instead of moving
files back to an earlier proposed structure:

| Language | Stored implementation root |
|---|---|
| Python | `practice/python/soutions/` |
| Rust | `practice/rust/solutions/` |
| TypeScript | `practice/typescript/` |
| JavaScript | `practice/javascript/` |
| Go | `practice/go/` |
| Bash | `practice/bash/` |
| Lua | `practice/lua/` |
| Lisp | `practice/lisp/` |

- [x] Retarget all 60 catalog paths and the independent coverage audit to these
      explicit roots, without counting native blank exercises as implementations.
- [x] Repair authored Markdown file/directory links and fragments, using existing
      inventory/lifecycle guides for the absent aggregate Solutions guide.
- [x] Remove dead legacy-test/package instructions instead of redirecting them to
      unrelated active tests or restoring intentionally removed files.
- [x] Remove legacy Make/package targets for the absent Python application; retain
      the shared Rust build/install/run and virtual Python development environment.
- [x] Fix TypeScript sibling module links and isolate nested Rust Users Cargo
      metadata without adding a test harness, dependency, or native adapter.
- [x] Add regression audits for local Markdown targets/anchors, TypeScript relative
      imports, and Python development-configuration paths.

At the link-cleanup milestone the six exercise bindings, shared question-document
locations, JSON export schema, and manual-check workflow were unchanged. Historical validation numbers
above refer to their respective earlier layouts, not to deleted legacy tests.

**Current-layout validation:** all 148 root integration/regression tests and 14
Rust unit tests passed, with formatting, Clippy (warnings denied), locked offline
build, and diff checks. The new audits cover repository-local Markdown links and
anchors, all 16 TypeScript relative imports, and virtual Python test configuration.
Nested Users Cargo metadata resolves independently without launching the server.
External web URLs and TypeScript test execution are not certified by these checks.

## Paired Python/Rust curated batch

Deliver the complete bounded curated set together, not one port at a time. This
does not convert the other 32 inventory topics or add another language adapter.

- [x] Register all five questions in both languages: Hello World, Find in String,
      Length of Last Word, Binary Search, and Fibonacci (ten native bindings).
- [x] Add the four missing Rust blank files without overwriting existing exercises.
      Preserve the intentional Python-print/Rust-return Hello binding difference.
- [x] Give each Rust exercise an explicit Cargo target and selected harness, keeping
      automatic target discovery disabled. Missing or broken siblings do not block
      the selected exercise; whole-track success requires every selected check.
- [x] Enforce declared Rust APIs through marked typed function assignments, with
      learner signature/name/visibility errors distinguished from broken harnesses.
- [x] Check matching contract edges across languages: ASCII first-match indexing,
      six standard ASCII whitespace separators and long words, signed-32-bit search
      boundaries/duplicates/input preservation, and all 41 Fibonacci lengths.
- [x] Publish five checked Python and five checked Rust examples under the existing
      implementation roots' `curated/` directories. Reuse their text only as inputs
      in disposable fixtures; expected outputs remain independently defined.
- [x] Preserve all 60 legacy artifacts. The inventory now has 70 artifacts, of which
      the ten new examples carry explicit native-test evidence, not a proof of all
      behavior. No stored solution is automatically copied into learner files.
- [x] Validate selected checks, both language sessions, wrong-contract/API mutants,
      zero/ignored tests, sibling isolation, branch guards, and per-file reset.
- [ ] Review and integrate the four new canonical Rust blanks into local main before
      using reset for those paths. The six existing blank paths already have baselines.

**Validation:** 162 isolated integration/regression tests passed with Python 3.15.
All 16 Rust units passed on Rust 1.85 and 1.89. Root and native harness formatting,
Clippy with warnings denied, locked offline build, local links, and diff checks
passed. Native published examples are checked after copying into temporary
exercises, not by modifying real attempts. Independent example probes and wrong,
missing, or private API checks also passed with Cargo/Rust 1.85. Runtime validation is macOS; Linux
runtime validation remains open. No servers, databases, watch mode, or persistent
progress were introduced.

## Practice and curriculum discipline throughout

These remain learning choices, not prerequisites for the two-language technical
proof. Two adapters do not imply two mandatory learning tracks.

- Choose one primary learning language and a concrete capability to improve.
- Keep a small Current Practice section in an existing programming hub in Darkness:
  focus, concept-note reference, exercise link, and one next action.
- Complete a few sessions and retry without consulting the solution. Record only
  useful discoveries or misconceptions in existing notes.
- Add the next useful exercise after identifying a learning need, not to fill a
   language-by-concept matrix. Give it a shared question, native blank, and check.
- Link or repair relevant note references as they are used; avoid bulk migration.

## Deferred, not required

- Database-backed mastery and automated next-exercise selection.
- Watch mode, file-save monitoring, and automatic/background checks. Manual
  checks are an intentional workflow decision, not an unfinished feature.
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

Review the paired-track batch on an authoring branch and integrate the four new
Rust blanks into main for canonical reset. Then use the complete curated set in
either language, choosing meaningful practice rather than more infrastructure.
`questions --pretty` distinguishes full-library inventory from runnable bindings
and checked examples. Practice remains manual; no watch mode is planned. Preserve
older attempts until copied and verified. No real-checkout commits, branch changes,
or merges are performed automatically.
