# Rust CLI: shared practice workflow

[Home](../README.md) · [Architecture](architecture.md) · [Roadmap](../ROADMAP.md)

## Overview

This implements the shared practice workflow and a line-based session.
Python and Rust share prompt/hint presentation, navigation, and check orchestration.
Manual checks are intentional: save, then explicitly check. There is no auto-run
on save or automatic advancement; watch mode is neither implemented nor planned.
`polyglot` is the only supported practice CLI. The root Python prototype and
obsolete starter/test files are retired, with no prototype fallback.

Practice uses tracked, independent `exercises/` files on Git practice branches
to keep `main` pristine. Ignored legacy answers are preserved if present;
the shared Rust CLI never imports or uses them and does not migrate solutions.
See [Exercise lifecycle](exercises.md) and
[ADR 0002](decisions/0002-pristine-main-practice-branches.md).

**Reset prerequisite:** the reviewed canonical blank must already be committed at
its exercise path in local `refs/heads/main`. New or uncommitted exercise paths
are not a baseline; reset fails safely until they are integrated. There is no
working-tree, learner-HEAD, or legacy-starter fallback, and no automatic commit.
All four current blank files already have this committed baseline on local main;
no additional baseline commit is needed for them. Newly authored files still need
reviewed integration into main before reset can restore them.

## Build

Requires Rust/Cargo 1.85+ to build. Python checks require Python 3.11+; listing and
starting do not require an installed Python interpreter or exercise toolchain.

From the repository root:

```sh
cargo build --locked
./target/debug/polyglot --help
```

The direct dependencies are `serde_json` and, on macOS/Linux, `rustix` for safe
filesystem operations during reset. The first build may need
network access to download locked dependencies. Once cached, the CLI can also be
built with `cargo build --offline --locked`. Rust exercise checks themselves use
an isolated dependency-free Cargo package and run offline and locked.

## Install the development binary locally

```sh
make install
polyglot practice
```

Like the other local development tools, this builds the **debug** binary and
installs it with executable permissions as `~/.local/bin/polyglot`, replacing an
existing installed copy. `make install-dev` is an alias; neither target installs
the unrelated experimental `pylearn` package. `make install-python` installs that
package, not the retired root prototype or the active practice CLI.

The install target creates the destination directory if needed, but does not
change PATH. If it is not on PATH, invoke `~/.local/bin/polyglot` directly.
Rerun `make install` after source changes; the installed binary is a copy, not a
symlink. It uses the build checkout as its default root even when run elsewhere.

Both paths can be overridden (including paths containing spaces):

```sh
make install INSTALL_DIR="/path/to/dev/bin" TARGET_DIR="/path/to/build/cache"
```

`TARGET_DIR` defaults to `CARGO_TARGET_DIR` when set, otherwise `target`. The build
passes that directory explicitly to Cargo and installs its native debug binary.
`make build` builds without installing; plain `make` still displays help.
This is a local development install, not release packaging.

## API / Interfaces

### List, start, check

```sh
./target/debug/polyglot list
./target/debug/polyglot list --language python
./target/debug/polyglot list --language rust

./target/debug/polyglot practice python/hello
./target/debug/polyglot practice rust/hello
```

For one-shot selection, first create or select a non-`main` branch, then use
`start ID`, edit the displayed file, and run `check ID`. `start` will not silently
switch branches. It validates and displays an existing **Exercise file:**; it
does not copy a template or launch an editor. A missing exercise requires reset
from the committed-main baseline. Standalone `check` never initializes an attempt.

The other Python IDs are `python/find_in_string` and
`python/length_of_last_word`. `check python` and `check rust` check a whole track.
Python uses independent `practice/python/exercises/{hello,find_in_string,length_of_last_word}.py`
modules and corresponding `tests/test_*.py` files. Rust uses
`practice/rust/exercises/hello.rs`, imported by `checks.rs`. Selecting another
exercise does not reset your work. Track READMEs document the contracts; the CLI displays each exercise's
prompt and hint from its catalog metadata.

The catalog is deliberately built in. It describes exercise IDs and native check
selectors separately from workspace mappings. There is currently one workspace
per language; independent workspace metadata should be introduced when a second
workspace within one language is needed, not through a plugin framework now.

## Example usage

### Practice in a session

```sh
./target/debug/polyglot practice
./target/debug/polyglot practice python
./target/debug/polyglot practice rust
./target/debug/polyglot practice python/find_in_string
```

Without a target, choose `python`/`rust` or `1`/`2` at the language menu. Quit or
EOF before selection creates no file or branch. Entering a session validates the
selected exercise, preserves existing work, and displays the exercise, position,
exercise file, and task. Hints appear only when requested.

Edit and save the displayed file in your own editor. The session does not open an
editor, monitor saves, or automatically run checks.

| Session command | Behavior |
|---|---|
| Enter, `check`, `c` | Check the selected exercise; stay on it |
| `hint`, `h` | Show a hint, not a full solution |
| `prompt` | Repeat the task |
| `reset`, `r` | Confirm reset of only the selected exercise from committed main |
| `next`, `n` | Recheck current source; advance only if it passes |
| `previous`, `p` | Move back without requiring a pass |
| `list`, `l` | List exercises in the selected language |
| `language python`, `language rust` | Switch to that language's first exercise |
| `help`, `?` | Show session commands |
| `quit`, `q`, EOF | End the session without changing exercise files |

`next` does not trust an earlier pass: it checks again, including after an external
edit. At the last exercise it reports `End of track` and stays there; it does not
wrap or claim every exercise has been completed. Validation must succeed before
navigation changes the selection. Switching languages preserves exercise files.

Failed, blocked, and indeterminate checks leave the session usable. Clean quit/EOF
returns `0` because the session ended normally, **not** because the exercises all
passed. Use one-shot `check` for a machine-readable check exit code.

There is no saved selection or progress; a new session starts at its requested
target or language menu. Edits during an active native process are not tracked
or used to invalidate that running result. Finish editing and save before checking
or resetting; do not edit while either operation is running. Optional persisted
resume would be considered only if needed, not as a prerequisite for retirement.

## Read a prompt or hint without starting

```sh
./target/debug/polyglot show python/find_in_string
./target/debug/polyglot hint rust/hello
```

These commands do not create attempts or launch language tools. `show` displays
the task and exercise path without revealing the hint; `hint` displays only the hint.

## Reset one exercise

The committed-main prerequisite in the overview must be met before these work:

```sh
polyglot reset python/hello
polyglot reset rust/hello
```

Reset accepts exactly one language-qualified exercise ID: no track, `all`, or
`--yes` option. Session `reset`/`r` uses the same implementation. It requires a
non-main branch; main is blocked with exit `2`. Only `y`/`yes` confirms (ignoring
case and surrounding whitespace). Cancellation/EOF returns `0` without writes.
Already-pristine source returns `0` without prompting or creating backups.

Reset resolves strict local `refs/heads/main` to a full commit OID once, before
prompting, and reads the raw committed regular-file blob with Git replacement
objects disabled. A moving main ref cannot change that reset's chosen baseline.
Missing refs, missing paths, symlinks, and non-regular tree entries are blocked;
no working-tree, learner-HEAD, or starter fallback exists.

Changed existing bytes are backed up under ignored `.polyglot/backups` before
atomic replacement. Keep both printed paths: **Backup:** is a byte snapshot;
**Recovery:** retains the displaced original inode, so an editor holding an open
descriptor can still write to it after replacement. New backup files use `0600`
and new private directories use `0700`. If the inode cannot safely move across
filesystems, a private adjacent recovery artifact remains at the exact printed
path. Do not delete it. There is no automatic backup/recovery cleanup. Restoring
a missing file creates no backup because no previous file exists.

Branch or source changes detected while prompting block without overwriting the
source. A late atomic editor save during exchange is different: the baseline may
already be installed when reset reports **Blocked**, and the actual displaced
bytes are retained at the reported backup/recovery paths. Do not assume every
Blocked result leaves the original source path untouched; read the diagnostic.
Preserve both artifacts, especially if an editor may still have a descriptor open.

Reset changes only the selected worktree file: staged content/index, Git history,
and Git configuration remain unchanged. It is not `git reset`. The native backend
supports macOS and Linux only; unsupported platforms or filesystem atomic
primitives block without an overwrite fallback. Runtime testing has covered macOS;
the Linux implementation has not been runtime-tested.

## Pristine main and practice branches

`practice` requires the root of a Git checkout/worktree with a committed named
HEAD. It creates a unique `practice/<language>-...` branch from clean `main`, or
reuses your existing non-`main` branch. Your branch remains selected after quitting;
the CLI does not switch you back or discard work.

Dirty `main` is blocked, including untracked files other than ignored files. If
you want to carry that work onto a branch, do so explicitly with an unused name:

```sh
git switch -c practice/my-session
polyglot practice
```

Branch preparation does not stash, discard work, commit, fetch, or force branch
changes. Explicit exercise reset is separate and described above. Detached or
unborn HEAD, bare/non-repositories, and a root nested inside another repo are
blocked. Existing ignored legacy attempts remain intact.

Session checks and navigation refuse to proceed if you externally switch to
`main`. Hints, prompts, listing, and quitting remain available. Standalone
list/show/hint/check are permitted on main and do not require Git.

To add protection against direct exercise commits on main:

```sh
make install-hooks
```

This explicitly installs the tracked pre-commit guard, not a Git configuration
change. It refuses to replace existing different hooks or configured hook systems;
identical installed guards are recognized. Updating the tracked source does not
replace an already-installed older guard; integrate changes manually with that
setup. No hook is installed by `make install`.
The guard checks staged protected active exercise source paths, including new
files, modifications, deletes, and renames, without
modifying your files or index. See ADR 0002 for the protected paths and limits.

This is not a filesystem lock: editors can still modify files and local hooks can
be bypassed. The guard covers active exercises and legacy ignored answer paths,
not retired starter paths.
Remote branch protection must be managed separately. Use a practice branch even
when running native commands directly.

## Roots and tool selection

The default root is the checkout where the binary was built. It does not depend on
the current working directory. To use another checkout, provide an explicit root.
All global options must come **before** the command:

```sh
/path/to/polyglot --root "/path/to/checkout" list
/path/to/polyglot --root "/path/to/checkout" --python "/path/to/python3" check python/hello
/path/to/polyglot --root "/path/to/checkout" --cargo "/path/to/cargo" check rust/hello
```

Python selection is `--python` → checkout `.venv/bin/python` (or
`.venv/Scripts/python.exe`) → `python3` on PATH. The selected interpreter and
version are displayed. An explicitly selected or existing repository interpreter
that cannot run is blocked; it does not silently fall back after failure.

Cargo selection is `--cargo` → `cargo` on PATH. Paths may contain spaces; tools
are invoked as argument vectors without shell interpolation. No command installs
tools, creates environments, or downloads exercise dependencies automatically.

## Data Flow

`model.rs` provides the static `Exercise` catalog (ID, file, language, title,
prompt, hint, native selector). `workspace.rs` validates common inputs plus only
the selected exercise/harness. Python's `exercises/__init__.py` has no re-exports:
broken or missing unselected sibling modules/tests do not block a selected check.
For example, hello selects `tests.test_hello.PracticeTests.test_hello`.
The Python adapter launches a fresh-source helper with a separate result report;
Rust uses Cargo JSON and the selected libtest executable (`hello`). Checks do not
trust learner stdout as a pass signal. The catalog does not discover new files.

## Edge Cases

### Outcomes and safety

| Exit code | Meaning |
|---|---|
| `0` | For `check`, selected checks ran and passed; other commands completed normally |
| `1` | An attributable learner-code or assertion failure |
| `2` | Invalid input or a blocked check: missing tools, bad target/configuration |
| `3` | Interrupted or indeterminate: no trustworthy normal result |

Native diagnostics are preserved. Ambiguous errors are not automatically blamed
on the learner. Zero selected tests and ignored/skipped checks do not pass.
Python uses fresh source and a separate result report rather than trusting learner
stdout; Rust uses Cargo compiler messages and the selected native test executable.
Rust outcome detection relies on Cargo JSON and stable libtest inventory/result
text, not a universal diagnostic parser.

- `start` validates an existing exercise and preserves it; it creates no file.
- `check` never initializes or resets an attempt. It may write normal Rust build
  artifacts, but locked checks do not update source inputs or lockfiles.
- Workspace symlinks and existing symlinks inside the isolated Rust build tree are
  rejected before native execution. This protects against existing path mistakes,
  not hostile concurrent filesystem replacement.
- Learner code runs with your privileges. This is not a sandbox for untrusted packs.
- General notes in Darkness are never loaded or edited by this proof.

Direct native check commands remain in the [Python](../practice/python/README.md)
and [Rust](../practice/rust/README.md) instructions.

## Verify the implementation

```sh
cargo fmt --all -- --check
cargo test --locked
cargo clippy --locked --all-targets -- -D warnings
cargo build --locked
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

The integration suite needs Python 3.11+ and Cargo on PATH. It runs the built
`target/debug/polyglot`; set `POLYGLOT_BIN` to test a different binary. A missing
binary fails with build instructions rather than silently skipping the suite.
The fixtures are isolated temporary copies, with temporary Git repositories where
needed, paths with spaces, and unrelated working directories. Active fixture
selection and explicit solution cases live in `tests/active_fixture.py`; tests do
not copy, reset, or check real local learner answers. Retired prototype tests are
not part of the active suite and are not required for authoring validation.
Unix-specific symlink/shim cases are skipped on other platforms. Runtime platform
validation so far is macOS only; this is not a full test run of older projects
under `src/`.

## Scope and deferrals

No persistent progress, editor launching, TUI, or release distribution. Watch mode
is deliberately out of scope, not a future delivery gate. The local debug install
above is supported. No Rustlings code was copied for these slices.
Tracked exercise files and explicit single-exercise reset are implemented. Reset
requires the reviewed canonical blank to be committed at its path in local
`refs/heads/main`. The root Python prototype is retired. Upstream pinning would be
needed if upstream code were copied; none was copied here. Learning exercises,
not a general platform, remain the scope.

## Related files

- [Exercise authoring and preservation](exercises.md)
- [Python track](../practice/python/README.md), [Rust track](../practice/rust/README.md)
- [Catalog](../cli/src/model.rs), [workspace validation](../cli/src/workspace.rs),
  [workflow](../cli/src/workflow.rs), [session](../cli/src/session.rs)
- [Git policy/baseline](../cli/src/git.rs), [reset](../cli/src/reset.rs),
  [native filesystem backend](../cli/src/reset/native.rs)
