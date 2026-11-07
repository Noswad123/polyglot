# Bash practice track

[Home](../../README.md) · [Shared CLI](../../README/rust-cli.md) · [Exercise lifecycle](../../README/exercises.md)

## Overview

One active binding, `bash/hello`, uses the shared
[Hello World contract](../../README/katas/hello_world.md). Use **Bash 3.2+**, not
an arbitrary `sh`. No dependencies or database are needed. The original flat
Hello World and Pong files remain unverified inventory, not learner exercises.
Read-only metadata commands need no installed Bash.

## API / Interfaces

Define shell function `hello` in [exercises/hello.sh](exercises/hello.sh). A call
must write exactly `Hello, World!` followed by one newline to stdout and finish
with status `0`. Sourcing the file must produce no stdout; do not add a top-level
demo. The adapter selects `--bash PATH` or `bash` on PATH and validates its version.
Global options, including `--root`, precede the command.

## Data Flow

The adapter copies only the selected exercise and [harness](tests/check_hello.sh)
into private scratch, syntax-checks the harness, and runs Bash with `--noprofile
--norc`. It removes `BASH_ENV`, `ENV`, and `SHELLOPTS` from the child environment.
The backend creates a private source-stdout capture file; the harness sources the
exercise into that file, verifies the function exists, calls it, checks status and
load-time output, and writes a separate completion report. The backend compares
function stdout byte-for-byte, preserving every trailing newline. A printed pass
word is not evidence of success. Use the shared CLI to manage these files.

## Edge Cases

The blank returns `1` deliberately. Missing functions, source failures, nonzero
function status, top-level output, wrong capitalization, or missing/extra newlines
fail. Broken harness syntax blocks checking. Calling `exit` can prevent the
completion report and yields an indeterminate result, not a pass. Learner code runs
with your privileges; this is not a sandbox.

Keep main canonical and edit on a practice branch. `practice` creates a branch only
from clean main or reuses an existing non-main branch; dirty main blocks without
stashing. `start`/`reset` require an existing non-main branch. Newly added blanks
must be reviewed and committed at their paths on local main before reset works.
Save before checking/resetting and do not edit during either. There is no watch
mode, automatic advancement, persisted progress, or database.

## Example usage

From the root after building/installing the shared CLI:

```sh
polyglot list --language bash
polyglot show bash/hello
polyglot practice bash/hello
# Edit and save the displayed file, then press Enter to check.
```

On an existing non-main branch:

```sh
polyglot start bash/hello
polyglot check bash/hello
polyglot check bash
polyglot --bash /bin/bash check bash/hello
```

Running the exercise as a script alone does not call its function or grade it.
After the committed-main prerequisite is met, `polyglot reset bash/hello` confirms
a single-file reset; preserve the printed backup and recovery artifacts.

## Related files

- [Shell adapter](../../cli/src/adapters/shell.rs), [bindings](../../cli/src/model.rs)
- [Checked example](solutions/curated/hello_world.sh): compare after attempting;
  checked against current native tests, not proof of all behavior. Root tests copy
  its text into disposable learner files, never real attempts.
- [Native regressions](../../tests/test_additional_hello.py), [full inventory](../../README/katas/index.md)
