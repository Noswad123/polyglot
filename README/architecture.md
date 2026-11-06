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

Python and Rust adapters resolve their tools, invoke the selected native checks,
and return evidence-backed outcomes: passed, attempt failed, blocked, or
interrupted/indeterminate. Keep native diagnostics; do not mistake missing tools
for an incorrect solution or zero selected tests for success.

The two built-in adapters now use the same list/start/check path; there is no
dynamic plugin framework. The initial catalog uses one workspace per language,
with independent files and native selectors for each exercise. Python's package
initializers do not import siblings. Add independent workspace metadata when a
second workspace within one language needs it.
Reuse suitable Rustlings patterns/code without importing Cargo assumptions into
application state or adopting a full fork by default.

## Example usage

```sh
cargo build --locked
./target/debug/polyglot list
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
- `cli/src/model.rs`: catalog, workspace mappings, native selectors, and outcomes.
- `cli/src/workflow.rs`: shared preparation, metadata display, and check orchestration.
- `cli/src/session.rs`: language selection and in-memory prompt/hint/navigation policy.
- `cli/src/workspace.rs`: contained paths and existing exercise-file validation.
- `cli/src/reset.rs` and `cli/src/reset/native.rs`: shared confirmation, canonical
  reset, descriptor-anchored file transactions, backups, and recovery.
- `cli/src/adapters/`: tool resolution, native invocations, and classification.

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
All four current blank files are already committed on local main. Newly authored
files still need reviewed integration there before they become reset baselines.
After confirmation, only the selected worktree file is restored. Its staged
version, other files, and Git refs are unchanged.

## Edge Cases

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
remain available but, like editors, do not enforce branch safeguards. The unrelated
`src/python/pylearn` package, `pyproject.toml`, uv tooling, and `make install-python`
remain experiments, not active practice entry points.

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
