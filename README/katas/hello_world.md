# Hello World

## Overview

Problem ID: `hello-world`. Produce the exact greeting `Hello, World!`.
This is the authoritative shared question; each binding specifies how the greeting
is observed. Printing and returning are intentionally different here.

## API / Interfaces

| Binding | Native interface | Observable contract |
|---|---|---|
| `python/hello` | `hello() -> None` | Print exactly `Hello, World!` followed by one newline; return `None`. |
| `rust/hello` | `pub fn greeting() -> &'static str` | Return exactly `Hello, World!`, without a newline. Printing is not a substitute. |
| `typescript/hello` | `export function hello(): void` | Synchronously print exactly `Hello, World!` followed by one newline; return `undefined`. |
| `go/hello` | `func Hello() string` in `package exercises` | Return exactly `Hello, World!`, without a newline. Printing is not a substitute. |
| `bash/hello` | Shell function `hello` | Print exactly `Hello, World!` followed by one newline; finish with status `0`. |
| `lua/hello` | Global function `hello()` | Print exactly `Hello, World!` followed by one newline; return no values or a single `nil`. |

**Readiness:** all six bindings above have native blanks and checks. JavaScript
and Lisp remain inventory-only; there is no JavaScript practice track. Existing
source examples alone do not establish readiness or committed reset baselines.

## Data Flow

The CLI reads this shared Markdown, then displays the selected language binding.
Edit the selected native exercise, not the preserved solution. Python checks
capture stdout and inspect the return value; Rust checks inspect the returned text.
Language-specific hints live in the CLI catalog, not in this question.
TypeScript uses the real compiler API and an exact static `() => void` probe,
then checks synchronous runtime output and return value. Go uses a typed function
assignment and the isolated `TestHello` test. TypeScript, Bash, and Lua use separate
completion reports and backend-managed file stdout capture, not learner output as
a pass signal. Use the CLI to supply that capture, especially for TypeScript and Lua.

## Edge Cases

Capitalization, comma, space, and exclamation mark are significant. Python must
not add extra output or extra newlines. Rust's returned string must not contain a
newline. These bindings share greeting text, not identical observable behavior.
TypeScript, Bash, and Lua must not print while importing, sourcing, or loading the
exercise: the greeting must come from the function call. Async TypeScript functions,
missing/default-only exports, wrong signatures, and non-`undefined` returns fail.
Lua returning two `nil` values fails, as does Bash printing correctly with a nonzero
status. Extra or missing newlines fail the printing bindings.

## Example usage

- Python: calling `hello()` produces stdout `"Hello, World!\n"` and returns `None`.
- Rust: calling `greeting()` returns `"Hello, World!"`.
- TypeScript/Bash/Lua: calling `hello` produces stdout `"Hello, World!\n"`;
  the return/status requirements above also apply.
- Go: calling `Hello()` returns `"Hello, World!"`.

```sh
polyglot question hello-world
polyglot show python/hello
polyglot show rust/hello
polyglot show typescript/hello
polyglot show go/hello
polyglot show bash/hello
polyglot show lua/hello
```

## Related files

- [Question library](index.md), [CLI catalog](../../cli/src/model.rs)
- [Python blank](../../practice/python/exercises/hello.py), [native checks](../../practice/python/tests/test_hello.py)
- [Rust blank](../../practice/rust/exercises/hello.rs), [native checks](../../practice/rust/checks.rs)
- Track setup and checks: [TypeScript](../../practice/typescript/README.md),
  [Go](../../practice/go/README.md), [Bash](../../practice/bash/README.md),
  [Lua](../../practice/lua/README.md).
- Checked examples: [Python](../../practice/python/soutions/curated/hello_world.py),
  [Rust](../../practice/rust/solutions/curated/hello_world.rs) (function `greeting`).
  Compare after attempting; checked against current native tests, not proof of all behavior.
- Checked Hello examples: [TypeScript](../../practice/typescript/solutions/curated/hello_world.ts),
  [Go](../../practice/go/solutions/curated/hello_world.go),
  [Bash](../../practice/bash/solutions/curated/hello_world.sh),
  [Lua](../../practice/lua/solutions/curated/hello_world.lua), with the same evidence limits.
- [Related Python solution](../../practice/python/soutions/hello_world.py) — unverified inventory; compare after attempting, not a blank.
