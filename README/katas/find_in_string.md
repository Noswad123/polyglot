# Find in String

## Overview

Problem ID: `find-in-string`. Return the zero-based index of the **first** occurrence
of a substring in a string, or `-1` when absent. Matching is case-sensitive.
This document is the authoritative shared behavior; language bindings specify the
native API and any behavior beyond the shared ASCII scope.

## API / Interfaces

Active binding: `python/find_in_string`:
`find_in_string(string: str, substring: str) -> int`.
Return an integer, not a boolean. Built-in string operations are allowed.

**Readiness:** question contract ready; Python has a native blank and checks.
Rust has no binding for this question. The older Python and TypeScript source
implementations are references, not additional active adapters or practice blanks.

## Data Flow

The CLI displays this shared Markdown plus the selected binding. The native check
passes a string and substring to the exercise and compares its return value with
the expected index. Hints remain in the CLI catalog; reference modules are not the
active check inputs.

## Edge Cases

- An empty substring matches at `0`, even when the input string is empty.
- An empty string with a nonempty substring returns `-1`.
- A substring longer than the string returns `-1`.
- Repeated or overlapping matches still return the first index.
- Cross-language conformance examples use ASCII. Python counts Unicode code
  points; JavaScript string indexing uses UTF-16 code units. A new binding must
  explicitly decide Unicode index units rather than imply universal equivalence.
  Bindings may extend naturally beyond ASCII, but that is not a shared guarantee
  or a claim that a JavaScript implementation has been tested.

## Example usage

| String | Substring | Result |
|---|---|---|
| `"Dawson, Jamal"` | `"Jamal"` | `8` |
| `"banana"` | `"ana"` | `1` |
| `"abc"` | `"abc"` | `0` |
| `"abc"` | `"c"` | `2` |
| `"abc"` | `"A"` | `-1` |
| `"a"` | `"abc"` | `-1` |
| `"abc"` | `""` | `0` |
| `""` | `""` | `0` |
| `""` | `"a"` | `-1` |

```sh
polyglot question find-in-string
polyglot show python/find_in_string
```

## Related files

- [Question library](index.md), [CLI catalog](../../cli/src/model.rs)
- [Python blank](../../practice/python/exercises/find_in_string.py), [native checks](../../practice/python/tests/test_find_in_string.py)
- Related solutions (unverified): [Python](../../practice/python/soutions/find_in_string.py), [TypeScript](../../practice/typescript/findTheIndexOfTheFirstOccurrenceInAString.ts)
- The Python reference prints an import-time demo; active checks do not import it.
