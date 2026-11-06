# Rust practice proof exercise

[Home](../../README.md) · [Rust CLI](../../README/rust-cli.md) · [Exercise lifecycle](../../README/exercises.md)

## Overview

One small exercise proves that the shared workflow can run native Rust checks as
well as Python. This is not a complete Rust track or a requirement to study Rust
alongside another language. Use Rust/Cargo 1.85+.

The active file is tracked `practice/rust/exercises/hello.rs`. Keep `main`
pristine; implement solutions on a practice branch, not in a separate answers file.

**Reset prerequisite:** the reviewed canonical blank must already be committed
at its exercise path in local `refs/heads/main`. New or uncommitted paths are not
a baseline; reset safely refuses until it exists. `start` does not create missing
files or copy a starter.

## API / Interfaces

For CLI ID `rust/hello`, implement this function in **`exercises/hello.rs`**:

```rust
pub fn greeting() -> &'static str
```

Return exactly `Hello, World!`; printing is not sufficient. The canonical blank
body uses `todo!()`. Hint: a string literal has a static lifetime.

## Data Flow

`checks.rs` imports `exercises/hello.rs` and calls `greeting()` in native test
`hello`. The independent, dependency-free Cargo package has a checked-in lockfile
and runs offline and locked. Normal build artifacts go in `practice/rust/target/`;
checks do not update source, harness, manifest, or lockfile.

`start` validates and displays **Exercise file:** without copying a template or
opening an editor. `practice` creates a unique branch from clean `main` or reuses
your non-main branch. Dirty `main` is refused without stashing. One-shot `start`
and `reset` require an existing non-main branch; standalone checks may run on main.

## Example usage

From the repository root:

```sh
cargo build --locked
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
resetting and do not edit during either operation; watching is not implemented.
Reset changes only the selected worktree file, not the staged version. Preserve
both `Backup:` and `Recovery:` artifacts; there is no automatic cleanup.

Legacy `starter.rs` and ignored `answers.rs` remain untouched for preservation
and compatibility. The shared Rust CLI and active `checks.rs` never import or use
them. No user solutions were automatically copied or migrated. To reuse an older
attempt, follow the [manual preservation steps](../../README/exercises.md#preserve-an-older-attempt).

## Related files

- [Exercise](exercises/hello.rs), [checks](checks.rs), [manifest](Cargo.toml), [lockfile](Cargo.lock)
- [Catalog](../../cli/src/model.rs), [Rust adapter](../../cli/src/adapters/rust.rs)
- Existing Rust notes in Darkness are optional; no notes database is required.
