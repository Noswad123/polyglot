# Rust practice proof exercise

[Home](../../README.md) · [Rust CLI](../../README/rust-cli.md) · [Exercise lifecycle](../../README/exercises.md)

## Overview

One small exercise proves that the shared workflow can run native Rust checks as
well as Python. This is not a complete Rust track or a requirement to study Rust
alongside another language. Use Rust/Cargo 1.85+.
The [full collection inventory](../../README/katas/index.md) exposes 37 topic
families through `polyglot questions`, but only `rust/hello` is active Rust practice.
Legacy Rust source is unverified reference inventory, not another binding or adapter.
The preserved [Users project](solutions/users/) lives in its own standalone
workspace, retaining its `src/` nesting and support files. It is not part of these
checks; do not start its server or touch its database to validate native practice.

The active file is tracked `practice/rust/exercises/hello.rs`. Keep `main`
pristine; implement solutions on a practice branch, not in a separate answers file.

**Reset prerequisite:** the reviewed canonical blank must already be committed
at its exercise path in local `refs/heads/main`. New or uncommitted paths are not
a baseline; reset safely refuses until it exists. `start` does not create missing
files or copy a starter.

## API / Interfaces

| Exercise ID | Shared question / problem ID | Native API |
|---|---|---|
| `rust/hello` | [hello-world](../../README/katas/hello_world.md) | `pub fn greeting() -> &'static str` |

Implement this binding in **`exercises/hello.rs`**. The shared question is
authoritative: Rust returns the greeting, while Python prints and returns `None`.
This intentional difference preserves both native APIs. The canonical blank body
uses `todo!()`. Other curated questions have no active Rust binding yet.

## Data Flow

`checks.rs` imports `exercises/hello.rs` and calls `greeting()` in native test
`hello`. The independent, dependency-free Cargo package has a checked-in lockfile
and runs offline and locked. Normal build artifacts go in `practice/rust/target/`;
checks do not update source, harness, manifest, or lockfile.

`show` and session `prompt` read the full shared question Markdown and display it
with the native language task; hints remain separate. `start` validates the
question and displays **Exercise file:** without copying a template or
opening an editor. `practice` creates a unique branch from clean `main` or reuses
your non-main branch. Dirty `main` is refused without stashing. One-shot `start`
and `reset` require an existing non-main branch; standalone checks may run on main.

## Example usage

From the repository root:

```sh
cargo build --locked
./target/debug/polyglot question hello-world
./target/debug/polyglot show rust/hello
./target/debug/polyglot practice rust/hello
# Edit and save practice/rust/exercises/hello.rs, then press Enter to check.
```

On a non-main branch, `polyglot start rust/hello` and `polyglot check rust/hello`
provide a one-shot loop. `check rust` currently selects the same single exercise.
See [tool selection](../../README/rust-cli.md#roots-and-tool-selection) for overrides.

Native checks do not enforce branch policy: select a practice branch yourself,
then run from the repository root:

```sh
cargo test --offline --locked --manifest-path practice/rust/Cargo.toml --test practice_checks -- hello --exact
```

After the committed-main prerequisite above is met, retry with
`polyglot reset rust/hello`, or `reset`/`r` in its session. Read the
[reset recovery contract](../../README/exercises.md#edge-cases) first.

## Edge Cases

Missing tools or broken check configuration are blocked checks, not failed
solutions. `check` does not initialize missing source. Save before checking or
resetting and do not edit during either operation. Explicit checks are intentional:
Enter/`check`/`c` checks and stays selected; `next`/`n` rechecks before advancing.
There is no auto-run on save, automatic advancement, or persisted progress, and
watch mode is neither implemented nor planned.
Reset changes only the selected worktree file, not the staged version. Preserve
both `Backup:` and `Recovery:` artifacts; there is no automatic cleanup.

Missing, empty, unreadable/non-UTF-8, non-regular, or symlinked curated Markdown
blocks `question`, `show`, `start`, and session entry/navigation before automatic
branching or committing a navigation selection. `list`, `questions`, `hint`, and
native checks do not require that Markdown. Edits to the question in the selected
checkout are visible without rebuilding; static catalog/native signature changes
require rebuilding and reinstalling the CLI.
For library-only topics, `question ID` permits empty drafts with a notice and
missing-question metadata without a prompt; it never reads or executes references.

The obsolete `starter.rs` is retired, as is the root Python prototype; `polyglot`
is the only supported practice CLI. Ignored `answers.rs` is preserved if present,
with its ignore and optional hook protection. The CLI and active `checks.rs` never
import or use it. No user solutions were automatically copied or migrated. To reuse
an older attempt, follow the [manual preservation steps](../../README/exercises.md#preserve-an-older-attempt).

## Related files

- [Exercise](exercises/hello.rs), [checks](checks.rs), [manifest](Cargo.toml), [lockfile](Cargo.lock)
- [Catalog](../../cli/src/model.rs), [Rust adapter](../../cli/src/adapters/rust.rs)
- [Shared question library](../../README/katas/index.md)
- [Collection layout and execution limits](../../README/exercises.md#collection-layout-and-execution-limits)
- Darkness remains canonical for general concept notes; repository questions own
  exercise instructions. No notes database is required.
