# Binary Search

## Overview

Problem ID: `binary-search`. Implement the **binary search algorithm** to determine
whether a target integer is present in an ascending-sorted array of integers.
Return boolean presence, **not an index**, and do not mutate the input array.
This document defines shared behavior; native names and types belong to bindings.

## API / Interfaces

Active binding: `python/binary_search`:
`binary_search(target: int, arr: list[int]) -> bool`. The target is the first
argument. Return `True` or `False`, not an integer index or diagnostic message.

**Readiness:** question contract ready; Python has a native blank and checks.
Rust is pending: no native binding exists for this question. The completed
`practice/python/soutions/binary_search.py` is an unverified solution with diagnostic printing, not
the canonical practice blank.

## Data Flow

The CLI shows this Markdown and the selected language binding. Native checks call
the selected exercise with a target and sorted array, compare boolean results,
and check that the array remains unchanged. Checks validate behavior, not algorithmic
complexity; passing them does not replace the requirement to use binary search.
Implementation hints remain in the CLI catalog.

## Edge Cases

- An empty array returns `False`.
- Duplicates are allowed; only presence matters.
- Handle singleton arrays, both endpoints, and misses between or outside values.
- Unsorted input is outside the contract. Tests must not require an exception or
  sorting the input; no unsorted-input behavior is specified.

## Example usage

| Target | Array | Result |
|---|---|---|
| `1` | `[1, 3, 5, 7, 9]` | `True` |
| `5` | `[1, 3, 5, 7, 9]` | `True` |
| `9` | `[1, 3, 5, 7, 9]` | `True` |
| `6` | `[1, 3, 5, 7, 9]` | `False` |
| `0` | `[1, 3, 5, 7, 9]` | `False` |
| `10` | `[1, 3, 5, 7, 9]` | `False` |
| `42` | `[]` | `False` |
| `4` | `[4]` | `True` |
| `5` | `[4]` | `False` |
| `2` | `[2, 2, 2, 2]` | `True` |

```sh
polyglot question binary-search
polyglot show python/binary_search
```

## Related files

- [Question library](index.md), [CLI catalog](../../cli/src/model.rs)
- [Python blank](../../practice/python/exercises/binary_search.py), [native checks](../../practice/python/tests/test_binary_search.py)
- [Related solution](../../practice/python/soutions/binary_search.py) — separate from the active practice harness; not certification against this contract. The old legacy tests were removed.
