# Rust practice track

[Home](../../README.md) · [Rust CLI](../../README/rust-cli.md) · [Exercise lifecycle](../../README/exercises.md)

## Overview

Five independent exercises use the same shared contracts and workflow as Python,
with native Rust checks. This is a small practice path, not a complete curriculum
or a requirement to study Rust alongside another language. Use Rust/Cargo 1.85+.
The [full collection inventory](../../README/katas/index.md) exposes 37 topic
families through `polyglot questions`; all five curated questions are active Rust practice.
Legacy Rust source is unverified reference inventory, not another binding or adapter.
The preserved [Users project](solutions/users/) lives in its own standalone
workspace, retaining its `src/` nesting and support files. It is not part of these
checks; do not start its server or touch its database to validate native practice.

Active files are `practice/rust/exercises/*.rs`. Keep `main`
pristine; implement solutions on a practice branch, not in a separate answers file.

**Reset prerequisite:** the reviewed canonical blank must already be committed
at its exercise path in local `refs/heads/main`. New or uncommitted paths are not
a baseline; reset safely refuses until it exists. `start` does not create missing
files or copy a starter.
Catalog registration does not establish a committed baseline; check local main's
committed tree before relying on reset for any newly authored path.

## API / Interfaces

| Exercise ID | Shared question / problem ID | Native API |
|---|---|---|
| `rust/hello` | [hello-world](../../README/katas/hello_world.md) | `pub fn greeting() -> &'static str` |
| `rust/find_in_string` | [find-in-string](../../README/katas/find_in_string.md) | `pub fn find_in_string(string: &str, substring: &str) -> isize` |
| `rust/length_of_last_word` | [length-of-last-word](../../README/katas/lengthOfLastWord.md) | `pub fn length_of_last_word(text: &str) -> usize` |
| `rust/binary_search` | [binary-search](../../README/katas/binarySearch.md) | `pub fn binary_search(target: i32, arr: &[i32]) -> bool` |
| `rust/fibonacci` | [fibonacci](../../README/katas/fibonacci.md) | `pub fn fibonacci(length: usize) -> Vec<u32>` |

Implement each binding in `exercises/<ID suffix>.rs`, in the order above. Shared
question Markdown is authoritative; native task strings do not duplicate it.
Hello returns the exact greeting without a newline, while Python prints it with
one newline and returns `None`. Canonical Rust blanks use `todo!()`; the four new
blanks do not overwrite the existing Hello or Python exercises.

## Data Flow

The dependency-free Cargo package has five explicit, isolated test targets and a
checked-in lockfile. Automatic library, binary, and test discovery is disabled
(`autolib = false`, `autobins = false`, `autotests = false`). Each harness includes
only its own exercise:

| Exact test selector | Cargo target | Harness |
|---|---|---|
| `hello` | `practice_checks` | `checks.rs` (retained path) |
| `find_in_string` | `find_in_string_checks` | `tests/find_in_string.rs` |
| `length_of_last_word` | `length_of_last_word_checks` | `tests/length_of_last_word.rs` |
| `binary_search` | `binary_search_checks` | `tests/binary_search.rs` |
| `fibonacci` | `fibonacci_checks` | `tests/fibonacci.rs` |

The adapter consumes typed `RustCheck { target, selector, harness }` metadata and
builds only the selected target, offline and locked. Broken or missing unselected
exercise files or harnesses do not block that check. Normal build artifacts go in `practice/rust/target/`;
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
provide a one-shot loop. `check rust` runs all five bindings sequentially and may
stop at the first non-pass; all five must pass for track success.
See [tool selection](../../README/rust-cli.md#roots-and-tool-selection) for overrides.

Native checks do not enforce branch policy: select a practice branch yourself,
then run from the repository root:

```sh
cargo test --offline --locked --manifest-path practice/rust/Cargo.toml --test practice_checks -- hello --exact
cargo test --offline --locked --manifest-path practice/rust/Cargo.toml --test find_in_string_checks -- find_in_string --exact
cargo test --offline --locked --manifest-path practice/rust/Cargo.toml --test length_of_last_word_checks -- length_of_last_word --exact
cargo test --offline --locked --manifest-path practice/rust/Cargo.toml --test binary_search_checks -- binary_search --exact
cargo test --offline --locked --manifest-path practice/rust/Cargo.toml --test fibonacci_checks -- fibonacci --exact
```

For a direct whole-package check, all five sources and harnesses must be valid:

```sh
cargo test --offline --locked --manifest-path practice/rust/Cargo.toml --tests
```

This intentionally builds all targets; it is not the isolated selected-check path.
`practice_checks` is Hello's target, not an aggregate target for all five exercises.

After the committed-main prerequisite above is met, retry with
`polyglot reset rust/hello`, or `reset`/`r` in its session. Read the
[reset recovery contract](../../README/exercises.md#edge-cases) first.

## Edge Cases

Shared text inputs are printable ASCII plus SPACE, TAB, LF, CR, VT (`\v`/`\x0b`),
and FF (`\f`/`\x0c`). Other Unicode/control-separator behavior is not guaranteed
across languages. Rust's checked last-word example uses `split_whitespace`, not
`split_ascii_whitespace` (which misses VT). See the separate CLI hints for guidance,
not full solutions in question bodies. Binary Search uses signed 32-bit values,
including `i32::MIN`/`i32::MAX`, without mutation and with manual interval halving;
behavioral tests do not prove complexity. Fibonacci checks all 41 lengths in
`0..=40`, returning exactly N terms starting `1, 1` (empty at zero); behavior beyond
that domain is unspecified.

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

- [Exercises](exercises/), [Hello checks](checks.rs), [other checks](tests/), [manifest](Cargo.toml), [lockfile](Cargo.lock)
- Checked examples (compare after attempting): [Hello World](solutions/curated/hello_world.rs)
  (function `greeting`, unlike the `hello.rs` blank filename),
  [Find in String](solutions/curated/find_in_string.rs),
  [Length of Last Word](solutions/curated/length_of_last_word.rs),
  [Binary Search](solutions/curated/binary_search.rs), [Fibonacci](solutions/curated/fibonacci.rs).
  Each is checked against current native tests, not proof of all behavior. Root
  tests read these files as text into disposable learner sources, never overwrite
  user attempts, and use independent expected outputs. This does not certify the
  legacy Users project or record user progress; browsing executes no examples.
- [Catalog](../../cli/src/model.rs), [Rust adapter](../../cli/src/adapters/rust.rs)
- [Shared question library](../../README/katas/index.md)
- [Collection layout and execution limits](../../README/exercises.md#collection-layout-and-execution-limits)
- Darkness remains canonical for general concept notes; repository questions own
  exercise instructions. No notes database is required.
