# Target architecture

[Home](../README.md) · [Roadmap](../ROADMAP.md)

**Accepted direction:** a Rust-hosted, Rustlings-inspired shared workflow with
native language adapters. The Rust list/start/check proof is implemented for
Python and Rust. A shared line-based session now supplies prompts, hints, and
navigation and canonical per-exercise reset. Manual checking is the intended
workflow, not an interim step toward watching. The root Python prototype is retired;
`polyglot` is the only supported practice CLI. See
[ADR 0001](decisions/0001-shared-workflow-language-adapters.md) for the decision,
boundaries, and adoption status.

## Overview

**Darkness = knowledge. Polyglot = practice. The CLI = access. A web UI is optional.**

Polyglot is one practice system with an interface, not a backend product and a CLI
product that must be completed independently.

```text
You
 |
Shared Rust workflow
select → edit → check → hint → next
 |
Exercise definition + safe workspace preparation
 |
Language adapter -------- native language tools
 |                           Python / Cargo / ...
Polyglot practice files
 |
references to concepts
 |
Darkness
```

The references are links, not a requirement to import notes into a shared database.

## Darkness: authoritative knowledge

Darkness owns explanations, mental models, language comparisons, resources,
personal learning goals, and learning takeaways. It answers:

> What does this mean, and what have I learned?

Small illustrative snippets belong here when useful. Full runnable exercise
solutions and test infrastructure belong in Polyglot.

## Polyglot: executable practice

Polyglot owns blank exercise modules, prompts, checks, runnable examples, and
practice-branch attempts. It
answers:

> What can I practice, and did this attempt work?

The initial storage is files in this repository. A future attempt/review history
would belong to Polyglot, not to a concept note's completeness status. Passing one
exercise is evidence about an attempt, not a declaration of mastery.

No backend service or database is needed for the current practice path. A future
storage choice should follow a concrete requirement, not precede it.

## API / Interfaces

The Rust workflow owns selection, safe preparation, check orchestration, feedback,
and shared hints/navigation policy. The line-based session uses explicit checks;
there is no watch mode or plan to add one. Persisted resume is optional future work
only if needed, not a retirement gate.
It must not contain Cargo/Python command construction or assume `.rs` files.

Exercise definitions connect stable IDs to workspaces, prompts, hints, native check
selectors, and optional notes. Multiple exercises can share one workspace; native
layouts need not be identical across languages.

A shared `Problem` in `library.rs` owns the problem ID, title, question status,
optional question-document path, and reference metadata (language, path, optional note).
`Exercise` references that problem and adds the language, source file, native API
task, hint, and check selector. Common behavior/examples live in
`README/katas/*.md`, not repeated language prompt strings. The retained directory
name preserves old links; its index separates curated contracts from drafts and
reference inventories. Intentional binding differences, such as Python printing
Hello World while Rust returns the greeting, are documented explicitly.

The static library covers 37 topic families: five curated, 15 draft, and 17 missing
questions; its 20 documents and 70 source artifacts (60 unverified legacy files plus
ten checked examples) are distinct from the ten active bindings in `model.rs`:
all five curated questions in Python and Rust. Reference labels span eight languages;
the native `Language` enum still has only Python and Rust. A curated question may
exist without a binding: contract readiness, reference availability, native practice,
and committed reset baselines are independent dimensions.

The shared workflow reads question Markdown at runtime. `questions` defaults to a
strict JSON metadata array; `questions --json` remains an explicit alias. Neither
adds a human header or footer to stdout, and the metadata schema and
repository-relative path format is unchanged; solution paths now use
the mixed `practice/` collection roots. The legacy JSON key `references` and its
language/path/nullable-note entries remain; no `solutions` alias is added.
`questions --pretty` means an ASCII
table, not pretty-printed JSON: within 80 columns, `Problem ID`, `Question`
(status), wrapped `Solutions` languages (the same 18-character column), and `Practice` native languages (or `-`
for not converted) replace verbose rows without duplicating the title. Its footer
gives aggregate totals including 70 solution artifacts and a “not all checked” legend with detail
commands. JSON or `question ID` retains titles, exact binding IDs, and full source
paths. Mixed or repeated format flags are rejected. `question PROBLEM_ID`
displays curated contracts, warns before draft bodies, or reports metadata and
reference paths when no document is registered. An empty draft succeeds with a
notice. Declared documents must still be readable UTF-8 regular files with no
symlink components. Active `show`/start/session selection requires a curated,
nonempty contract, validated before automatic branching; native checks and metadata
listing remain document-independent. Discovery never reads/imports/executes legacy
references, requires no Git/tools/root files, and is not a runtime filesystem audit.
General reference notes remain in Darkness; question contracts belong to Polyglot.

Preserved implementations live under `practice/`: Python uses `python/soutions/`,
Rust Users uses `rust/solutions/users/`, and other language collections are flat
apart from retained project subdirectories. Checked examples additionally live in
`practice/python/soutions/curated/` and `practice/rust/solutions/curated/`.
Their reference notes record native-test evidence, not proof of all behavior;
the legacy JSON `references` key and nullable-note schema remain unchanged.
The old Python tests and compatibility
bridge were removed. This layout adds no adapters, changes no shared contracts,
and does not certify specs, servers, or database projects. See the
[lifecycle guide](exercises.md#collection-layout-and-execution-limits) for execution limits.

Python and Rust adapters resolve their tools, invoke the selected native checks,
and return evidence-backed outcomes: passed, attempt failed, blocked, or
interrupted/indeterminate. Keep native diagnostics; do not mistake missing tools
for an incorrect solution or zero selected tests for success.

The two built-in adapters now use the same list/start/check path; there is no
dynamic plugin framework. The initial catalog uses one workspace per language,
with independent files and native selectors for each exercise. Python's package
initializers do not import siblings. Add independent workspace metadata when a
second workspace within one language needs it.
Rust uses `NativeCheck::Rust(RustCheck { target, selector, harness })` metadata:
five explicit isolated Cargo targets, each including only its own exercise.
The adapter builds only the selected target; broken or missing siblings do not
block a selected check. Whole-track checks run sequentially, may stop at the first
non-pass, and pass only if all five pass. Cargo command construction stays in the
adapter, not language-specific workflow branches.
Reuse suitable Rustlings patterns/code without importing Cargo assumptions into
application state or adopting a full fork by default.

## Example usage

```sh
cargo build --locked
./target/debug/polyglot list
./target/debug/polyglot questions --pretty
./target/debug/polyglot practice python/hello
# After editing/checking in the session, quit; the practice branch stays selected.
./target/debug/polyglot check python/hello
./target/debug/polyglot practice rust/hello
```

See the [CLI instructions](rust-cli.md) for tool selection, root overrides,
outcome codes, preservation guarantees, and isolated test commands.

## Related files

Code boundaries are explicit:

- `cli/src/main.rs`: argument parsing and command dispatch.
- `cli/src/library.rs`: full static topic inventory, statuses, optional documents,
  and reference paths/notes distinguishing checked examples from legacy inventory.
- `cli/src/model.rs`: native exercise bindings, workspace mappings,
  selectors, and outcomes.
- `cli/src/workflow.rs`: shared preparation, metadata display, and check orchestration.
- `cli/src/session.rs`: language selection and in-memory prompt/hint/navigation policy.
- `cli/src/workspace.rs`: contained paths and existing exercise-file validation.
- `cli/src/reset.rs` and `cli/src/reset/native.rs`: shared confirmation, canonical
  reset, descriptor-anchored file transactions, backups, and recovery.
- `cli/src/adapters/`: tool resolution, native invocations, and classification.
- `README/katas/`: shared question contracts plus the explicit conversion backlog.
- `practice/`: native exercise workspaces, checked examples, and legacy collections; see the inventory for exact roots.
- `tests/test_library_inventory.py`: independent coverage audit of all 20 question
  documents and 70 source artifacts; coverage, not legacy solution validation.
- `tests/active_fixture.py`: reads all ten published examples as text and copies
  them into disposable learner sources for native-check regressions, never user attempts.

Native checks may produce build artifacts but must preserve learner sources and
locked inputs. Python checks execute fresh source instead of cached bytecode.
Missing tools/configuration are blocked, and ambiguous results are indeterminate.
This is a local practice tool, not a sandbox or arbitrary exercise-pack executor.

## Data Flow

[ADR 0002](decisions/0002-pristine-main-practice-branches.md) separates the canonical
exercise baseline on `main` from learner branches. `cli/src/git.rs` owns exact-root
checkout validation and branch policy, not the language adapters. Practice creates
a branch only from clean main; direct start requires an existing non-main branch.
Session actions revalidate after external branch changes. Standalone checks remain
available for validating canonical material.

An opt-in pre-commit guard protects staged exercise paths on main. It is not
automatically installed, is not a filesystem lock, and does not replace remote
branch policy. It covers active exercise sources and legacy ignored answer paths,
not retired starters. Tracked guard updates do not replace already-installed old
hooks; the installer refuses different existing hooks or configured hook systems.
No Git configuration or remote settings are changed by the CLI.

Active practice now uses tracked per-exercise modules. `start` validates an
existing file without copying templates. Obsolete starters and their shared test
harness are retired. Legacy ignored answer files are preserved if present and are
not imported or migrated by the CLI.

Reset requires a non-main branch, pins strict local `refs/heads/main` once, and
reads the actual regular-file blob with Git object replacements disabled. Missing
canonical files block; uncommitted files or learner HEAD are never fallbacks.
The six existing blank files have committed baselines. Newly authored
files still need reviewed integration there before they become reset baselines.
This includes the four new Rust blanks until their canonical blobs reach local main.
After confirmation, only the selected worktree file is restored. Its staged
version, other files, and Git refs are unchanged.

## Edge Cases

Shared text contracts cover printable ASCII plus SPACE, TAB, LF, CR, VT, and FF.
Other Unicode/control-separator behavior is not cross-language guaranteed. Binary
Search's shared numeric scope is signed 32-bit; Python integers can be broader.
Fibonacci uses exactly N terms starting `1, 1` for `0..=40`; behavior outside that
domain is unspecified. The question Markdown remains authoritative, rather than
duplicating full contracts in native task strings. Contract curation, native
practice readiness, stored-example validation, reset readiness, and user progress
are separate dimensions.

The macOS/Linux backend uses no-follow directory handles and conditional atomic
operations. Changed existing files receive private snapshot backups and a lasting
original-inode recovery artifact, so an editor's held descriptor cannot write into
an inode that reset later discards. Late races or post-exchange failures report
recovery paths and disclose whether the baseline was installed; do not assume
every blocked result left source unchanged. Unsupported platforms/filesystems
fail closed rather than using a destructive fallback. See the
[lifecycle guide](exercises.md) for prerequisites, retention, and authoring.

Session checks and one-shot checks use the same context and adapters. `next`
rechecks before advancing, while `check` stays on the selected exercise. There is
no saved pass used as a navigation gate; selection and language switches are
committed only after safe preparation succeeds. Finish editing and save before
checking/resetting; do not edit during either operation. Saves do not trigger
checks, and passing does not automatically advance or persist progress. Session
quit success does not mean all checks passed.

## Historical prototype retirement

The root `polyglot.py` prototype and obsolete practice starters/tests are retired;
there is no prototype fallback. `make install` installs the Rust debug binary at
`~/.local/bin/polyglot`; release packaging remains separate. Direct native checks
remain available but, like editors, do not enforce branch safeguards. The former
`pylearn` package, other language packages under `src/`, and the unused root database
experiment were removed. Root Python configuration is development/test tooling,
not an installed runtime package or CLI.

## Integration rules

- General explanations remain in Darkness; exercise contracts remain in Polyglot.
- Note references are optional. A missing note or unavailable MindWeaver index
  must not prevent starting or checking an exercise.
- The CLI does not automatically edit notes or synchronize statuses.
- Existing local attempts must never be silently overwritten.
- Direct native check commands remain documented even when a CLI shortcut exists.
- Practice must not depend on a web service, notes database, or progress service.
- The Rust host explicitly resolves its Python interpreter rather than assuming
  the host process already supplies one.
- Checks are explicitly requested after saving; no file watchers or auto-run on
  save are planned. Any future optional resume must not treat old passes as current
  validity or turn completion history into a mastery score.

## Later capabilities, not current promises

Once real practice demonstrates the need, the same CLI could provide note lookup,
attempt history, or an exercise-review queue. Reading through MindWeaver is one
possible note-lookup implementation, not a dependency we are adding now.

A UI could use the same exercise contracts later. There is no commitment to build
it, and it should not establish a second source of truth for exercises or notes.

The desired outcome is a short path into useful practice, not a comprehensive
learning-management platform. See the roadmap for the next decision gate.
