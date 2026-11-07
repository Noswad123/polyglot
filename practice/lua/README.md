# Lua practice track

[Home](../../README.md) · [Shared CLI](../../README/rust-cli.md) · [Exercise lifecycle](../../README/exercises.md)

## Overview

One active binding, `lua/hello`, uses the shared
[Hello World contract](../../README/katas/hello_world.md). Use **Lua 5.1+** with
regular-file stdout flush/seek support. No packages or database are required.
Original flat Hello World and Pong sources remain unverified inventory, not
converted exercises. Metadata commands are read-only and need no Lua toolchain.

## API / Interfaces

Define global function `hello()` in [exercises/hello.lua](exercises/hello.lua).
A call must print exactly `Hello, World!` followed by one newline and return either
no values or one `nil`. A local-only function is not the required global API;
returning text, `true`, or even two `nil` values fails. Loading the file must
produce no stdout. The adapter selects `--lua PATH` or `lua` on PATH, probing
`_VERSION` for Lua 5.1+. All global options, including `--root`, precede the command.

## Data Flow

The adapter copies only the exercise and [harness](tests/check_hello.lua) into
private scratch, preflights harness syntax, and removes shell startup variables,
`LUA_INIT`, and versioned `LUA_INIT_5_1` through `LUA_INIT_5_5`. The harness loads
the chunk, uses protected calls, measures load/function output through stdout
flush/seek, validates return arity, and writes a separate completion report.
The backend compares exact stdout bytes, including trailing newlines.

**Use `polyglot check`, not a bare Lua harness invocation.** The adapter supplies
an initially empty private regular-file stdout capture; a terminal or pipe does
not provide the required seek semantics. This also captures writes through a
saved `io.stdout` handle without replacing learner output functions.

## Edge Cases

The blank deliberately raises an error. Syntax/runtime errors, load-time output,
missing globals, wrong returns, and extra/missing newlines fail. Broken harnesses
or unavailable flush/seek support block checking. Early `os.exit` without a
trustworthy completion report is indeterminate, not a pass. This is not a sandbox.

Keep learner edits on a practice branch. `practice` branches only from clean main
or reuses an existing non-main branch; dirty main blocks without stashing.
`start`/`reset` require an existing non-main branch. A new blank must be reviewed
and committed at its path on local main before reset can restore it. Save before
checking/resetting and do not edit during either. Checks are manual: no watch mode,
automatic advancement, persisted progress, or database.

## Example usage

From the root after building/installing the shared CLI:

```sh
polyglot list --language lua
polyglot show lua/hello
polyglot practice lua/hello
# Edit and save the displayed file, then press Enter to check.
```

On an existing non-main branch:

```sh
polyglot start lua/hello
polyglot check lua/hello
polyglot check lua
polyglot --lua /path/to/lua check lua/hello
```

After the baseline prerequisite is met, `polyglot reset lua/hello` confirms a
single-file reset; preserve both printed backup and recovery artifacts.

## Related files

- [Shell adapter](../../cli/src/adapters/shell.rs), [bindings](../../cli/src/model.rs)
- [Checked example](solutions/curated/hello_world.lua): compare after attempting;
  checked against current native tests, not proof of all behavior. Root tests copy
  its text into disposable learner files, never real attempts.
- [Native regressions](../../tests/test_additional_hello.py), [full inventory](../../README/katas/index.md)
