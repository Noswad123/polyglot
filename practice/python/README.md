# Python practice track

[Home](../../README.md) · [Roadmap](../../ROADMAP.md) · [Exercise lifecycle](../../README/exercises.md)

## Overview

Five independent, tracked `exercises/` modules provide a small practice loop.
These are five active bindings, not the whole collection: `polyglot questions`
and the [full inventory](../../README/katas/index.md) expose all 37 topic families.
Drafts and code-only topics such as Boggle and Stack are discoverable but not
practice bindings; legacy references are unverified and never run by discovery.
Preserved implementations live in [`soutions/`](soutions/) (existing spelling),
with five new checked examples in [`soutions/curated/`](soutions/curated/), separate
from learner modules. All five shared contracts also have active Rust bindings.
Hello World additionally has TypeScript, Go, Bash, and Lua bindings; these are
Hello-only tracks, not conversion of their legacy collections. Native menu order
is Python, Rust, TypeScript, Go, Bash, Lua. JavaScript and Lisp remain inventory-only.
The old seven pytest files and
compatibility import bridge were removed, not migrated to these tests.
Use Python 3.11+; native checks need no package installation, virtual environment,
database, or CLI. Keep `main` pristine and edit exercises on a practice branch.
`polyglot practice python` creates a unique branch from clean `main`, or reuses
your non-main branch; dirty `main` is refused without stashing anything.

**Reset prerequisite:** the reviewed canonical blank module must already be
committed at its exercise path in local `refs/heads/main`. New or uncommitted
paths are not a baseline. Neither `start` nor `reset` invents a missing exercise
or copies a legacy starter; reset fails safely until the baseline is available.

## API / Interfaces

| Exercise ID | Shared question / problem ID | Native API |
|---|---|---|
| `python/hello` | [hello-world](../../README/katas/hello_world.md) | `hello() -> None` |
| `python/find_in_string` | [find-in-string](../../README/katas/find_in_string.md) | `find_in_string(string: str, substring: str) -> int` |
| `python/length_of_last_word` | [length-of-last-word](../../README/katas/lengthOfLastWord.md) | `length_of_last_word(text: str) -> int` |
| `python/binary_search` | [binary-search](../../README/katas/binarySearch.md) | `binary_search(target: int, arr: list[int]) -> bool` |
| `python/fibonacci` | [fibonacci](../../README/katas/fibonacci.md) | `fibonacci(length: int) -> list[int]` |

The [question library](../../README/katas/index.md) owns common contracts and
examples; these are native bindings, in track order. Each module is
`exercises/<ID suffix>.py`. Python's Hello binding prints and returns `None`,
while Rust's returns text; the intentional difference is specified in the question.
Binary Search returns presence, not an index, without changing its sorted input;
use binary search even though checks validate behavior, not complexity.
The shared integer range is signed 32-bit, including `-2147483648` and `2147483647`;
Python's broader integer range is not a cross-language guarantee.
Fibonacci takes a term count, not an upper-value cutoff. The linked question
defines its inclusive `0..40` domain and `1, 1` prefix; legacy references do not expand it.
Both languages' native checks cover all 41 lengths against fixed expected terms.

## Data Flow

The shared Rust CLI selects a static binding linked to a shared problem, reads its
question Markdown, validates the workspace and selected files, and displays
**Exercise file:**. `show` and session `prompt` display the full shared contract
plus the native language task; hints remain separate. `start` only selects an existing
file; it does not copy a template or launch an editor. Edit and save that module,
then explicitly check it with Enter/`check`/`c` in the session or a one-shot check.
Manual checking is intentional, not a step toward auto-run on save. Each test
imports only its corresponding exercise and shared
`tests/feedback.py`. `exercises/__init__.py` has no re-exports, so a broken or
missing unselected sibling does not block a selected check.

The CLI's hello selector is `tests.test_hello.PracticeTests.test_hello`; the other
selectors follow the same per-module/per-method naming. Track checks select all
five exercises (five test methods, with multiple cases). Native unittest commands
below run the same contracts directly.

## Example usage

From the repository root, after building/installing the [shared CLI](../../README/rust-cli.md):

```sh
polyglot list --language python
polyglot question binary-search
polyglot show python/binary_search
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
python3 -B -m unittest tests.test_binary_search
python3 -B -m unittest tests.test_fibonacci
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
or resetting; do not edit during either operation. Watch mode is neither implemented
nor planned. Checks stay on the selected exercise; `next`/`n` rechecks before
advancing. There is no automatic advancement or persisted progress.
A missing selected file requires restoration from the committed-main baseline,
not automatic starter copying. A selected check still requires its common package
and feedback files and its own test harness.

Missing, empty, unreadable/non-UTF-8, non-regular, or symlinked curated documents
block `question`, `show`, `start`, and session entry/navigation. Library-only draft
detail permits empty bodies with a notice, and missing-question detail shows only
metadata/reference paths. Neither makes a guessed binding runnable. The active question is
validated before automatic branching or committing a navigation selection.
`list`, `questions`, `hint`, and native checks do not require question Markdown.
Question edits in the selected checkout appear without rebuilding; static catalog
metadata and native-signature prompts require rebuilding/reinstalling the CLI.
Shared string inputs are printable ASCII plus SPACE, TAB, LF, CR, VT (`\v`/`\x0b`),
and FF (`\f`/`\x0c`). Python's `str.split()` naturally recognizes broader whitespace;
other Unicode/control separators are not cross-language guaranteed. Python uses
Unicode code points, not Rust byte offsets, UTF-16 units, or grapheme clusters.
New Unicode bindings must explicitly agree on units and whitespace rules rather
than assume cross-language equivalence. Fibonacci behavior outside `0..40` is unspecified.

The root Python prototype, `starter.py`, and shared `test_exercises.py` are retired;
`polyglot` is the only supported practice CLI. Ignored `answers.py` is preserved if
present, with its ignore and optional hook protection, but is never imported or
used by the CLI. Nothing has automatically migrated learner solutions; see the
[manual preservation steps](../../README/exercises.md#preserve-an-older-attempt).
The unrelated experimental Python package was also removed. Root Python
configuration is virtual development/test tooling, not a runtime package;
any retained `pylearn` metadata name does not provide a command or import.

## Related files

- [Catalog and selectors](../../cli/src/model.rs), [Python adapter](../../cli/src/adapters/python.rs)
- [Tests](tests/), [exercise modules](exercises/)
- Checked examples (compare after attempting): [Hello World](soutions/curated/hello_world.py),
  [Find in String](soutions/curated/find_in_string.py),
  [Length of Last Word](soutions/curated/length_of_last_word.py),
  [Binary Search](soutions/curated/binary_search.py), [Fibonacci](soutions/curated/fibonacci.py).
  Each is checked against current native tests, not proof of all behavior. Root
  fixtures read published examples as text and copy them into disposable learner
  sources, never user attempts; expected native outputs are independent. Browsing
  executes no example. This evidence neither certifies legacy files nor records
  user progress.
- Related solutions (unverified): [Hello World](soutions/hello_world.py),
  [Find in String](soutions/find_in_string.py),
  [Length of Last Word](soutions/length_of_last_word.py),
  [Binary Search](soutions/binary_search.py),
  [Fibonacci](soutions/fibonacci.py). Compare only
  after attempting. The older `lengthOfLastWord` splits on literal spaces, unlike
  this track's general-whitespace contract; the older search module prints a demo
  when imported, as does Fibonacci; Binary Search prints diagnostics. Active tests
  do not import these preserved attempts or copy them into canonical blanks.

For concept notes, use existing Darkness programming notes under
`autodactyl/computer-science/software/theoretical-computation/programming-concepts/`.
`function-definition`, `print-to-console`, and `string-interpolation` are possible
starting points. Keep focus/next actions in an existing programming hub; no note
metadata, progress database, or synchronization is needed to practice.
Darkness remains canonical for general concepts; repository question documents
own exercise instructions.
