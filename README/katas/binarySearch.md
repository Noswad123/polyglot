# Binary Search

## Overview

Problem ID: `binary-search`. Implement the **binary search algorithm** to determine
whether a target integer is present in an ascending-sorted array of integers.
Return boolean presence, **not an index**, and do not mutate the input array.
This document defines shared behavior; native names and types belong to bindings.

## API / Interfaces

| Binding | Native interface |
|---|---|
| `python/binary_search` | `binary_search(target: int, arr: list[int]) -> bool` |
| `rust/binary_search` | `pub fn binary_search(target: i32, arr: &[i32]) -> bool` |

The target is the first argument. Return a boolean, not an integer index or
diagnostic message. Implement interval halving manually rather than delegating to
a built-in binary-search operation.

**Readiness:** question contract ready; Python and Rust have native blanks and checks. The legacy
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
- Shared targets and elements are signed 32-bit integers, including `i32::MIN`
  (`-2147483648`) and `i32::MAX` (`2147483647`). Python integers have a broader
  range, but that does not expand the cross-language contract.
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
| `-2147483648` | `[-2147483648, 0, 2147483647]` | `True` |
| `2147483647` | `[-2147483648, 0, 2147483647]` | `True` |

```sh
polyglot question binary-search
polyglot show python/binary_search
polyglot show rust/binary_search
```

## Related files

- [Question library](index.md), [CLI catalog](../../cli/src/model.rs)
- [Python blank](../../practice/python/exercises/binary_search.py), [native checks](../../practice/python/tests/test_binary_search.py)
- [Rust blank](../../practice/rust/exercises/binary_search.rs), [native checks](../../practice/rust/tests/binary_search.rs)
- Checked examples: [Python](../../practice/python/soutions/curated/binary_search.py),
  [Rust](../../practice/rust/solutions/curated/binary_search.rs). Compare after
  attempting; checked against current native tests, not proof of all behavior or complexity.
- [Related solution](../../practice/python/soutions/binary_search.py) — separate from the active practice harness; not certification against this contract. The old legacy tests were removed.
