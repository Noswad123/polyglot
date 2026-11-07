# Length of Last Word

## Overview

Problem ID: `length-of-last-word`. Return the length of the final
whitespace-separated word, ignoring leading and trailing whitespace. All six
standard ASCII whitespace characters separate words: SPACE, TAB (`\t`), LF (`\n`),
CR (`\r`), VT (`\v`/`\x0b`), and FF (`\f`/`\x0c`). Repeated separators do not create words.
This is the authoritative shared question, independent of native function naming.

## API / Interfaces

| Binding | Native interface |
|---|---|
| `python/length_of_last_word` | `length_of_last_word(text: str) -> int` |
| `rust/length_of_last_word` | `pub fn length_of_last_word(text: &str) -> usize` |

**Readiness:** question contract ready; Python and Rust have native blanks and checks.
Older Python and TypeScript references
split on literal spaces and do **not** satisfy the full current whitespace
contract; they are not practice-ready bindings.

## Data Flow

The CLI displays the shared Markdown plus the selected binding. Native checks call
the exercise with text and inspect the returned integer. They do not import the
legacy references. Language-specific hints remain in the CLI catalog.

## Edge Cases

- Empty text or whitespace-only text returns `0` (the empty word list case).
- Leading/trailing whitespace is ignored, including CR, VT, and FF.
- Punctuation is part of a word and counts toward its length.
- Shared text inputs use printable ASCII plus the six whitespace characters above.
  Other Unicode/control separators are not cross-language guaranteed. Broader whitespace rules and
  character-count units require a binding decision; code points, UTF-16 code
  units, and user-perceived characters are not universally interchangeable.
  Natural language-specific extensions are not a shared guarantee.

## Example usage

Escapes in this table denote actual whitespace characters.

| Text | Result |
|---|---|
| `"Hello World"` | `5` |
| `"   fly me   to   the moon  "` | `4` |
| `"single"` | `6` |
| `"hello\tworld"` | `5` |
| `"hello\nworld\n"` | `5` |
| `"hello\rworld\r"` | `5` |
| `"hello\vworld\f"` | `5` |
| `"hello world!"` | `6` |
| `""` | `0` |
| `" \t\n"` | `0` |
| `" \t\n\r\v\f"` | `0` |

```sh
polyglot question length-of-last-word
polyglot show python/length_of_last_word
polyglot show rust/length_of_last_word
```

## Related files

- [Question library](index.md), [CLI catalog](../../cli/src/model.rs)
- [Python blank](../../practice/python/exercises/length_of_last_word.py), [native checks](../../practice/python/tests/test_length_of_last_word.py)
- [Rust blank](../../practice/rust/exercises/length_of_last_word.rs), [native checks](../../practice/rust/tests/length_of_last_word.rs)
- Checked examples: [Python](../../practice/python/soutions/curated/length_of_last_word.py),
  [Rust](../../practice/rust/solutions/curated/length_of_last_word.rs). Compare after
  attempting; checked against current native tests, not proof of all behavior.
- Related solutions (unverified): [Python](../../practice/python/soutions/length_of_last_word.py), [TypeScript](../../practice/typescript/lengthOfLastWord.ts)
