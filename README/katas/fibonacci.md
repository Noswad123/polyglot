# Fibonacci

## Overview

Problem ID: `fibonacci`. Return exactly the first **N values** of the Fibonacci
sequence beginning `1, 1`, where each subsequent value is the sum of the preceding
two. The input is a sequence length, not an upper-value cutoff.
This document is the authoritative shared question.

## API / Interfaces

Input: an integer length in `0..40`, inclusive. Return a list/sequence of integers;
do not print the sequence as the answer. These bounds keep all core values within
signed 32-bit integers.

Active binding: `python/fibonacci`: `fibonacci(length: int) -> list[int]`.

**Readiness:** question contract ready; Python has a native blank and checks.
No other native binding is active, including Rust or JavaScript. Existing source
implementations are unverified solution attempts, not practice blanks.

## Data Flow

The CLI renders this shared Markdown plus the selected binding. Native checks call
the exercise with a length and compare the returned sequence, including its length
and prefix values. Hints remain in the CLI catalog. Active checks do not import
the older source references or their demos.

## Edge Cases

- Length `0` returns `[]`; length `1` returns `[1]`; length `2` returns `[1, 1]`.
- Include exactly N values even when sequence values exceed N.
- No behavior is specified for negative lengths, nonintegers, or values above `40`.
  A reference accepting a broader domain does not expand the shared contract.
- The older Python reference agrees on prefix and length within the shared domain,
  accepts other lengths, and prints an import-time demo.
- The legacy JavaScript reference differs in both prefix and result length; it is
  not yet conforming to this question. Its code remains unmodified.

## Example usage

| Length | Returned sequence |
|---|---|
| `0` | `[]` |
| `1` | `[1]` |
| `2` | `[1, 1]` |
| `4` | `[1, 1, 2, 3]` |
| `8` | `[1, 1, 2, 3, 5, 8, 13, 21]` |

```sh
polyglot question fibonacci
polyglot show python/fibonacci
```

## Related files

- [Question library](index.md), [CLI catalog](../../cli/src/model.rs)
- [Python blank](../../practice/python/exercises/fibonacci.py), [native checks](../../practice/python/tests/test_fibonacci.py)
- Related solutions (unverified): [Python](../../practice/python/soutions/fibonacci.py), [JavaScript](../../practice/javascript/fibonacci.js)
- The old legacy Python tests were removed; they are not the native practice harness.
