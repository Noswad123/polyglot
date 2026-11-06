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

**Readiness:** question contract ready; Python and Rust have native blanks and
checks. Other languages need an explicit binding and native tests before becoming
active exercises. Existing source examples alone do not establish readiness.

## Data Flow

The CLI reads this shared Markdown, then displays the selected language binding.
Edit the selected native exercise, not the preserved solution. Python checks
capture stdout and inspect the return value; Rust checks inspect the returned text.
Language-specific hints live in the CLI catalog, not in this question.

## Edge Cases

Capitalization, comma, space, and exclamation mark are significant. Python must
not add extra output or extra newlines. Rust's returned string must not contain a
newline. These bindings share greeting text, not identical observable behavior.

## Example usage

- Python: calling `hello()` produces stdout `"Hello, World!\n"` and returns `None`.
- Rust: calling `greeting()` returns `"Hello, World!"`.

```sh
polyglot question hello-world
polyglot show python/hello
polyglot show rust/hello
```

## Related files

- [Question library](index.md), [CLI catalog](../../cli/src/model.rs)
- [Python blank](../../practice/python/exercises/hello.py), [native checks](../../practice/python/tests/test_hello.py)
- [Rust blank](../../practice/rust/exercises/hello.rs), [native checks](../../practice/rust/checks.rs)
- [Related Python solution](../../practice/python/soutions/hello_world.py) — unverified inventory; compare after attempting, not a blank.
