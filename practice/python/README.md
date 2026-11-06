# Python starter track

[Home](../../README.md) · [Roadmap](../../ROADMAP.md)

Use the shared Rust CLI's `polyglot practice python` for branch-aware practice:
it leaves clean main for a practice branch before preparing work. Direct native
commands and the older Python prototype below do not enforce that policy; select
a non-main branch yourself before using them. The current shared answer file is
transitional; tracked independent `exercises/` modules and reset are next.

Three small exercises to establish a repeatable practice loop. They adapt existing
katas without changing their reference solutions. Use Python 3.11+; no package
installation, virtual environment, database, or Polyglot CLI is required.

All commands below run from the repository root. `python3 --version` checks your
interpreter; an existing `.venv/bin/python` can also replace `python3`.

## Optional CLI shortcuts

The repository-local CLI wraps the same workflow:

```sh
python3 polyglot.py list --language python
python3 polyglot.py start python/hello
# Edit practice/python/answers.py, then:
python3 polyglot.py check python/hello
```

Use `python/find_in_string` or `python/length_of_last_word` for the other exercises,
or `python3 polyglot.py check python` for the whole track. All three exercises share
one answer file. Selecting another exercise preserves your current answers.

`start` prints the answer and prompt paths. `check` never initializes or resets
answers; if they are missing, it tells you how to start. Checks use the same Python
interpreter as the CLI and stop on the first failure. A failed test returns exit
code 1; invalid input or a missing attempt returns exit code 2.

The direct commands below remain an alternative; no CLI installation is required.

## Start an attempt

```sh
cp -n practice/python/starter.py practice/python/answers.py
```

Edit **`practice/python/answers.py`**, not the starter or tests. `cp -n` leaves an
existing attempt alone. Answers are ignored by Git so a personal attempt does not
replace the shared blank starter. Save a separate copy if you want to keep an
attempt's history; ignored answers are not backed up by commits.

The starter functions raise `NotImplementedError` deliberately. A failing check is
the starting point, not a broken installation. Run one exercise at a time so that
unfinished later exercises do not distract you.

## 1. Hello World

Implement `hello() -> None`.

- Print exactly `Hello, World!` followed by a newline.
- Return `None`.

```sh
python3 -m unittest discover -s practice/python -p test_exercises.py -k hello -v
```

This is primarily a setup check. If it is familiar, finish it quickly and move on.

## 2. Find in String

Implement `find_in_string(string: str, substring: str) -> int`.

- Return the zero-based index of the first occurrence.
- Return `-1` if no match exists.
- An empty substring matches at index `0`, including in an empty string.
- Matching is case-sensitive. Built-in string operations are allowed.

Examples: `("banana", "ana") → 1`, `("abc", "z") → -1`, `("abc", "") → 0`.

```sh
python3 -m unittest discover -s practice/python -p test_exercises.py -k find_in_string -v
```

## 3. Length of Last Word

Implement `length_of_last_word(text: str) -> int`.

- Return the length of the final whitespace-separated word.
- Ignore leading and trailing whitespace. Spaces, tabs, and newlines separate words.
- Empty or whitespace-only input returns `0`.
- Punctuation remains part of a word; this is not natural-language parsing.

Examples: `"Hello World" → 5`, `"  fly me to the moon  " → 4`, `" \t\n" → 0`.

```sh
python3 -m unittest discover -s practice/python -p test_exercises.py -k length_of_last_word -v
```

## Check the whole track

```sh
python3 -m unittest discover -s practice/python -p test_exercises.py -v
```

Each of the three test methods checks the exercise contract; the string exercises
include multiple cases. All three should pass after completing the track.

## Retry without losing other work

1. Save a copy of your answers if you want to preserve the attempt.
2. Replace only the function you want to retry with its body from `starter.py`.
3. Attempt it again without consulting the previous solution.
4. Run that exercise's check.

Do not copy the entire starter over an existing answer file unless you intend to
discard every answer. There is no automated destructive reset command.

## Connect practice to notes

Use the existing programming concept notes in Darkness, particularly
`autodactyl/computer-science/software/theoretical-computation/programming-concepts/`.
The `function-definition`, `print-to-console`, and `string-interpolation` notes
are possible starting references; add only insights that belong there.

Keep the current learning focus and next action in an existing programming hub.
No note metadata, progress status, or synchronization step is needed to run checks.

## Compare only after attempting

Existing implementations are references, not necessarily solutions to every edge
case in this track:

- [Hello World](../../src/python/katas/hello_world.py)
- [Find in String](../../src/python/katas/find_in_string.py)
- [Length of Last Word](../../src/python/katas/length_of_last_word.py)

The older last-word function is named `lengthOfLastWord` and separates words using
literal spaces. This track uses the Python-style name `length_of_last_word` and an
explicit general-whitespace contract. The older find-in-string module also prints
a demonstration when imported. The starter checks import only your local answers,
never those reference modules.
