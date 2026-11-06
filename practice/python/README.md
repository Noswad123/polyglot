# Python practice track

[Home](../../README.md) · [Roadmap](../../ROADMAP.md) · [Exercise lifecycle](../../README/exercises.md)

## Overview

Three independent, tracked `exercises/` modules provide a small practice loop.
Use Python 3.11+; native checks need no package installation, virtual environment,
database, or CLI. Keep `main` pristine and edit exercises on a practice branch.
`polyglot practice python` creates a unique branch from clean `main`, or reuses
your non-main branch; dirty `main` is refused without stashing anything.

**Reset prerequisite:** the reviewed canonical blank module must already be
committed at its exercise path in local `refs/heads/main`. New or uncommitted
paths are not a baseline. Neither `start` nor `reset` invents a missing exercise
or copies a legacy starter; reset fails safely until the baseline is available.

## API / Interfaces

| CLI ID | Exercise file under `practice/python/` | Function |
|---|---|---|
| `python/hello` | `exercises/hello.py` | `hello() -> None` |
| `python/find_in_string` | `exercises/find_in_string.py` | `find_in_string(string: str, substring: str) -> int` |
| `python/length_of_last_word` | `exercises/length_of_last_word.py` | `length_of_last_word(text: str) -> int` |

- **Hello:** print exactly `Hello, World!` and a newline; return `None`.
- **Find in String:** return the zero-based first occurrence, or `-1` if absent.
  Matching is case-sensitive; built-in operations are allowed. An empty substring
  matches at `0`, including in an empty string. Examples: `("banana", "ana") → 1`,
  `("abc", "z") → -1`, `("abc", "") → 0`.
- **Length of Last Word:** return the length of the final whitespace-separated
  word, ignoring surrounding whitespace. Spaces, tabs, and newlines separate
  words; empty/whitespace-only text returns `0`. Punctuation counts as part of a
  word. Examples: `"Hello World" → 5`, `"hello world!" → 6`, `" \t\n" → 0`.

## Data Flow

The shared Rust CLI selects a static catalog entry, validates the workspace and
selected files, and displays **Exercise file:**. `start` only selects an existing
file; it does not copy a template or launch an editor. Edit and save that module,
then check it. Each test imports only its corresponding exercise and shared
`tests/feedback.py`. `exercises/__init__.py` has no re-exports, so a broken or
missing unselected sibling does not block a selected check.

The CLI's hello selector is `tests.test_hello.PracticeTests.test_hello`; the other
selectors follow the same per-module/per-method naming. Track checks select all
three exercises. Native unittest commands below run the same contracts directly.

## Example usage

From the repository root, after building/installing the [shared CLI](../../README/rust-cli.md):

```sh
polyglot list --language python
polyglot practice python/hello
# Edit practice/python/exercises/hello.py; Enter checks in the session.
```

On an existing non-main branch, the one-shot alternative is:

```sh
polyglot start python/hello
polyglot check python/hello
polyglot check python
```

For native commands, select a practice branch yourself: unittest does not enforce
the branch policy. From `practice/python` run one module at a time:

```sh
python3 -B -m unittest tests.test_hello
python3 -B -m unittest tests.test_find_in_string
python3 -B -m unittest tests.test_length_of_last_word
```

From the repository root, check the whole track:

```sh
python3 -B -m unittest discover -s practice/python/tests -t practice/python -v
```

An existing `.venv/bin/python` can replace `python3`. Blank functions deliberately
fail until implemented. After the committed-main prerequisite above is met, retry
only one exercise with `polyglot reset python/hello`, or `reset`/`r` in its session.
Read the [backup and recovery contract](../../README/exercises.md#edge-cases)
before resetting; keep both printed backup and recovery paths.

## Edge Cases

`check` never initializes or resets source. Finish editing and save before checking
or resetting; do not edit during either operation. There is no watch mode.
A missing selected file requires restoration from the committed-main baseline,
not automatic starter copying. A selected check still requires its common package
and feedback files and its own test harness.

Legacy `starter.py`, `test_exercises.py`, and ignored `answers.py` (including any
user implementation) remain untouched for compatibility and preservation. They
are not imported or used by the shared Rust CLI. The older `python3 polyglot.py`
workflow remains a separate prototype, not the active workflow above. Nothing has
automatically migrated learner solutions; see the [manual preservation steps](../../README/exercises.md#preserve-an-older-attempt).

## Related files

- [Catalog and selectors](../../cli/src/model.rs), [Python adapter](../../cli/src/adapters/python.rs)
- [Tests](tests/), [exercise modules](exercises/)
- Reference implementations: [Hello World](../../src/python/katas/hello_world.py),
  [Find in String](../../src/python/katas/find_in_string.py),
  [Length of Last Word](../../src/python/katas/length_of_last_word.py). Compare only
  after attempting. The older `lengthOfLastWord` splits on literal spaces, unlike
  this track's general-whitespace contract; the older search module prints a demo
  when imported. Active tests do not import those references.

For concept notes, use existing Darkness programming notes under
`autodactyl/computer-science/software/theoretical-computation/programming-concepts/`.
`function-definition`, `print-to-console`, and `string-interpolation` are possible
starting points. Keep focus/next actions in an existing programming hub; no note
metadata, progress database, or synchronization is needed to practice.
