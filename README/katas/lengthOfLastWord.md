# Length of Last Word

## Overview

Problem ID: `length-of-last-word`. Return the length of the final
whitespace-separated word, ignoring leading and trailing whitespace. Spaces,
tabs, and newlines separate words; repeated separators do not create words.
This is the authoritative shared question, independent of native function naming.

## API / Interfaces

Active binding: `python/length_of_last_word`:
`length_of_last_word(text: str) -> int`.

**Readiness:** question contract ready; Python has a native blank and checks.
Rust has no binding for this question. Older Python and TypeScript references
split on literal spaces and do **not** satisfy the full current whitespace
contract; they are not practice-ready bindings.

## Data Flow

The CLI displays the shared Markdown plus the selected binding. Native checks call
the exercise with text and inspect the returned integer. They do not import the
legacy references. Language-specific hints remain in the CLI catalog.

## Edge Cases

- Empty text or whitespace-only text returns `0` (the empty word list case).
- Leading/trailing whitespace is ignored, including tabs and newlines.
- Punctuation is part of a word and counts toward its length.
- Shared conformance examples use ASCII. Broader Unicode whitespace rules and
  character-count units require a binding decision; code points, UTF-16 code
  units, and user-perceived characters are not universally interchangeable.
  Natural language-specific extensions are not a shared guarantee.

## Example usage

In this table, `\t` and `\n` denote actual tab and newline characters.

| Text | Result |
|---|---|
| `"Hello World"` | `5` |
| `"   fly me   to   the moon  "` | `4` |
| `"single"` | `6` |
| `"hello\tworld"` | `5` |
| `"hello\nworld\n"` | `5` |
| `"hello world!"` | `6` |
| `""` | `0` |
| `" \t\n"` | `0` |

```sh
polyglot question length-of-last-word
polyglot show python/length_of_last_word
```

## Related files

- [Question library](index.md), [CLI catalog](../../cli/src/model.rs)
- [Python blank](../../practice/python/exercises/length_of_last_word.py), [native checks](../../practice/python/tests/test_length_of_last_word.py)
- Related solutions (unverified): [Python](../../practice/python/soutions/length_of_last_word.py), [TypeScript](../../practice/typescript/lengthOfLastWord.ts)
