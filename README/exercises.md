# Exercise lifecycle and authoring

[Home](../README.md) · [Shared CLI](rust-cli.md) · [Branch policy ADR](decisions/0002-pristine-main-practice-branches.md)

## Overview

Canonical blank exercises live in tracked `practice/<language>/exercises/` files.
Learners edit those same files on practice branches; `main` remains pristine.
There is no separate `starters/` directory or active shared answers file. This is
a small learning workflow, not a general exercise-pack platform.

**Baseline prerequisite:** a reviewed canonical blank must be committed to local
`refs/heads/main` before reset can restore it. New or uncommitted exercise paths
are not a baseline. Until that commit exists, reset blocks safely; it does not
invent a blank or use the working tree, learner HEAD, or old starter. No automatic
commit or learner-solution migration is implied.

## API / Interfaces

| ID | Active file | Native selector |
|---|---|---|
| `python/hello` | `practice/python/exercises/hello.py` | `tests.test_hello.PracticeTests.test_hello` |
| `python/find_in_string` | `practice/python/exercises/find_in_string.py` | `tests.test_find_in_string.PracticeTests.test_find_in_string` |
| `python/length_of_last_word` | `practice/python/exercises/length_of_last_word.py` | `tests.test_length_of_last_word.PracticeTests.test_length_of_last_word` |
| `rust/hello` | `practice/rust/exercises/hello.rs` | `hello` in `practice_checks` |

`cli/src/model.rs` statically declares `Exercise` entries: language-qualified `id`,
workspace-relative `file`, `language`, `title`, `prompt`, `hint`, and `check`
(`NativeCheck` selector). Adding a file alone does not add an exercise to the CLI.
Ordinary exercises need catalog/test changes, not a new adapter branch.

## Data Flow

1. `practice` validates the selection and creates a unique practice branch from
   clean main, or reuses a non-main branch. Dirty main is refused without stash.
2. `start ID` validates an existing selected file and displays **Exercise file:**.
   It requires a non-main branch, copies no template, and launches no editor.
3. Save the selected module and check it. Python tests import only their own
   exercise and shared feedback; `exercises/__init__.py` has no re-exports.
   Broken/missing unselected siblings do not prevent selected checks. Rust
   `checks.rs` calls `greeting()` from `exercises/hello.rs`.
4. Retry explicitly with `reset ID` or session `reset`/`r`, after the baseline
   prerequisite above. Only that worktree file is restored; the index is unchanged.

Standalone checks and read-only commands are allowed on main. Native commands and
the legacy Python prototype do not enforce branch policy; select a practice branch
yourself. The optional `make install-hooks` staged-path guard covers protected
active source additions, modifications, deletions, and renames on main. It is not
an editor read-only lock, does not change remote protection, and installs no Git
configuration. Reset never changes Git configuration, history, or the index.

## Edge Cases

Reset accepts one explicit ID, never a track, `all`, or `--yes`. It resolves strict
local `refs/heads/main` to a full commit OID once before prompting, then reads the
raw regular-file blob with replacement objects disabled. Only `y`/`yes` confirms;
cancel/EOF returns `0` without writes. Already-pristine source returns `0` without
prompt/backups. Main is blocked (`2`). Missing exercise source can be restored
only if that committed baseline exists; restoration has no backup of a nonexistent
file.

For changed existing source, reset prints **Backup:** (snapshot) and **Recovery:**
(the lasting displaced original inode). Preserve both: held editor descriptors can
keep writing to the recovery inode even after reset finishes. Backups normally
live under ignored `.polyglot/backups`; new snapshot files use `0600`, new private
directories `0700`. If a safe cross-filesystem move is unavailable, a private
adjacent recovery artifact remains at the exact reported path. Do not delete that
artifact. Backups/recovery files have no automatic cleanup.

Normally the selected source is atomically replaced with canonical bytes. Source
or branch changes detected while prompting block without overwrite. A late atomic
edit during exchange can instead report **Blocked after the baseline is already
installed**, retaining actual displaced bytes at the reported paths. Do not assume
all Blocked results leave the original source untouched. The staged version remains
unchanged in either case. Read diagnostics and preserve recovery artifacts.

The native backend is macOS/Linux only; unsupported platforms/filesystem atomic
primitives block without an overwrite fallback. macOS has runtime coverage; Linux
implementation has not been runtime-tested. Save before checking/resetting and do
not edit while either runs: watching and superseded-run handling are not implemented.

## Example usage

With the shared CLI installed, from a clean canonical main:

```sh
polyglot practice python/hello
# Edit the displayed exercise file; Enter checks, hint shows guidance, next rechecks.
```

After the committed-main prerequisite is satisfied, on a non-main branch:

```sh
polyglot start python/hello
polyglot check python/hello
polyglot reset python/hello
```

### Preserve an older attempt

Legacy Python `starter.py`, `test_exercises.py`, and ignored `answers.py`, plus
Rust `starter.rs` and ignored `answers.rs`, remain untouched for compatibility and
preservation. The shared Rust CLI never imports or uses them. No solution has been
automatically copied or claimed migrated.

To reuse your own older solution, first select a practice branch. Manually copy
only the selected function and its needed imports into the corresponding active
exercise module; do not copy the whole old shared answers file or overwrite sibling
exercises. Save, run the selected check, and explicitly verify the saved contents
and any separate preservation copy. Keep the old file until that verification is
complete; ignored files are not protected by Git commits. Do not merge learning
solutions into main.

### Author a new exercise

1. From clean main, create an authoring branch, not a learning-solution merge.
2. Add a canonical blank module under the appropriate tracked `exercises/` path
   and an independent test harness. In Python, keep package initializers free of
   sibling re-exports. Update the track's contract documentation.
3. Add an `Exercise` catalog entry with its qualified ID, file, language, native
   selector, title, prompt, and hint. Reuse the existing language adapter for an
   ordinary exercise; no new adapter dispatch branch is needed.
4. In isolated fixtures, verify the blank fails for the intended reason and a
   valid implementation passes. Check selected isolation, including broken/missing
   siblings where applicable. Update `tests/active_fixture.py`'s explicit copy
   selection when needed and add a solution case for the new exercise.
5. Run the [full regression commands](rust-cli.md#verify-the-implementation),
   including legacy prototype coverage, against disposable fixtures, not personal
   attempts. Keep validated solutions in test fixtures, not canonical modules.
6. Submit for PR review. The reviewed canonical blank must reach local main's
   committed tree before it becomes a reset baseline. Never merge learning
   solutions into main.

No Rustlings code has been copied. Upstream version pinning becomes relevant only
if upstream code is copied; a learning-workflow resemblance alone requires none.

## Related files

- [Python contracts/native commands](../practice/python/README.md)
- [Rust contract/native command](../practice/rust/README.md)
- [Catalog and types](../cli/src/model.rs), [validation](../cli/src/workspace.rs)
- [Reset](../cli/src/reset.rs), [native backend](../cli/src/reset/native.rs), [Git baseline](../cli/src/git.rs)
- [Fixture copying/solutions](../tests/active_fixture.py), [CLI/session guide](rust-cli.md)
