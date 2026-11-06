# Polyglot
![Polyglot](./img/polyglot.png)

A personal programming practice space inspired by Rustlings: small exercises,
immediate feedback, and repeated attempts across the languages I'm studying.

**Darkness holds the explanations. Polyglot holds the executable practice.**

Start simple, practice often, and develop idiomatic fluency. Multiple languages
are welcome; implementing every concept in every language is not a requirement.

## Overview

The accepted direction is a **Rust-based shared workflow with native language
adapters**, preserving the Rustlings-style interaction across languages. See
[ADR 0001](README/decisions/0001-shared-workflow-language-adapters.md).

The [Rust CLI](README/rust-cli.md) supports the shared list/start/check workflow
for Python and Rust through separate native adapters, plus a line-based practice
session with prompts, hints, navigation, and per-exercise reset from committed
`main`. Python and Rust use tracked `exercises/` files instead of an active
shared answer file. `polyglot` is the only supported practice CLI; the root Python
prototype and obsolete starter/test files are retired. Existing ignored legacy
answers are preserved if present, with no automatic migration.

To build and use the shared CLI from the repository root:

```sh
cargo build --locked
./target/debug/polyglot list
./target/debug/polyglot practice
```

In the session, choose a language, edit the displayed exercise in your own editor,
then press Enter to check. Use `h` for a hint, `n` to recheck and advance after a
pass, `p` to go back, and `q` to quit. Manual checks are intentional: finish editing
and save before checking or resetting, and do not edit during either operation.
There is no auto-run on save, automatic advancement, or persisted progress.
Watch mode is neither implemented nor planned; persisted resume is optional future
work only if needed, not a prerequisite for retiring the prototype.

To install the development binary alongside other local tools:

```sh
make install
polyglot practice
```

This builds the Rust debug binary and installs it as `~/.local/bin/polyglot`.
Use `make install-dev` as an alias, or override `INSTALL_DIR`. The bin directory
must be on PATH to invoke `polyglot` by name. Rerun the target after code changes.
The installed binary remains bound to this checkout by default; use `--root` for
another checkout. `make install-python` installs the unrelated experimental
`pylearn` package, not the retired root prototype or the active practice CLI.

## Pristine main and practice branches

`main` is the canonical exercise baseline. `polyglot practice` creates a unique
practice branch from clean main, or reuses your current non-main branch. On dirty
main it stops without stashing or resetting anything. To carry existing work to
a branch explicitly, choose an unused name:

```sh
git switch -c practice/my-session
polyglot practice
```

`polyglot start` requires an existing non-main branch. Practice/start require the
exact root of a committed Git checkout or worktree, not detached HEAD. Read-only
commands and standalone checks remain available on main.

For an optional guard against direct exercise commits on main, run
`make install-hooks`. It does not change Git configuration or replace an existing
different hook. Updating the tracked guard does not update an already-installed
older hook; integrate changes manually with that setup. It cannot stop editor
changes, and local hooks can be bypassed; remote branch rules are a separate layer. See
[ADR 0002](README/decisions/0002-pristine-main-practice-branches.md).

The active files are now `practice/python/exercises/*.py` and
`practice/rust/exercises/hello.rs`. Current ignored legacy answer files are
preserved if present, not automatically split or imported. The optional guard
covers active `practice/*/exercises/**` paths and the two legacy answer paths,
not retired starter paths. Editor and native commands do not enforce branch safety.

On a practice branch, `polyglot reset python/hello` (or session `reset`/`r`) asks
before restoring only that exercise from a pinned commit of local `main`.
All four current blank files are already committed on local `main`; no additional
baseline commit is needed for them. A newly authored file still needs reviewed
integration into local `main` before reset can restore it; a working-tree file is
not enough. Uncommitted cleanup on main still makes it dirty and blocks automatic
practice-branch creation until you explicitly branch or reconcile those changes.
Changed existing files get private snapshot and original-inode recovery artifacts;
the index is unchanged. See the [exercise lifecycle guide](README/exercises.md)
before using reset or moving an older attempt into the new files.

## Start practicing

The [Python exercises](practice/python/README.md) are the first self-contained
practice path. It needs Python 3.11+ and no third-party packages or database.
Python is the initial working example, not a prescribed primary language.

From the repository root:

```sh
polyglot list --language python
polyglot practice python/hello
```

An unimplemented exercise should fail. Make that check pass, then follow the
[track instructions](practice/python/README.md) for the next exercise.
`start` validates the selected existing file; it creates or resets nothing.
Each exercise has its own module and test, so a broken sibling does not block an
individual check. Use `polyglot check python` to check the whole track. The Rust CLI
resolves Python explicitly; see `--python` and `--root` in its instructions.

Direct native commands remain in the track instructions; use them on a practice
branch too. They do not enforce the CLI's branch safeguards.

The three exercises are a small setup-and-feedback path, not a full curriculum:

1. **Hello World:** functions and observable output; skip quickly if familiar.
2. **Find in String:** return values and text searches.
3. **Length of Last Word:** text cleanup and edge cases.

## A practice session

1. Choose one small capability in one primary language.
2. Read the exercise contract; attempt it before looking at a solution.
3. Run its check, use the feedback, and try again.
4. Record a useful discovery in an existing Darkness note, if there is one.
5. Revisit the exercise later without the solution.

Use a familiar reference language only when comparison helps. Passing a test is
evidence about this attempt, not a claim of permanent mastery.

## What lives where

- **Darkness (`~/projects/darkness`):** concept notes, mental models, language
  comparisons, resources, personal learning priorities, and takeaways.
- **This repository:** blank exercise modules, prompts, checks, runnable code, and
  instructions needed to run it. Small illustrative snippets may still live in notes.
- **Polyglot CLI:** one front door for listing, starting, and checking practice.
  It delegates to native tools; it does not manage your notes or learning goals.
- **Optional platform work:** the older `pylearn` CLI, database, frontend, and
  backend remain separate experiments. `src/python/pylearn`, `pyproject.toml`, uv
  tooling, and `make install-python` are unrelated to the retired root prototype.
  None is required for the active practice tracks.

## Find your way around

- [Roadmap](ROADMAP.md): boundaries, phased work, acceptance criteria, and deferrals.
- [Target architecture](README/architecture.md): Darkness as knowledge, Polyglot as
  practice, and a shared Rust workflow with native adapters as the target.
- [Architecture decision](README/decisions/0001-shared-workflow-language-adapters.md):
  adapter boundaries, outcome semantics, and adoption status.
- [Pristine-main decision](README/decisions/0002-pristine-main-practice-branches.md):
  branch creation, direct-commit safeguards, and migration limits.
- [Shared Rust CLI](README/rust-cli.md): build/run instructions for both adapters,
  tool selection, safety, and outcome codes.
- [Exercise lifecycle and authoring](README/exercises.md): tracked files, safe reset,
  preserving older attempts, and creating or fixing exercises.
- [Python exercises](practice/python/README.md): prompts, checks, and retry instructions.
- [Rust proof exercise](practice/rust/README.md): a native check for the second adapter.
- [Existing language code](src/): katas, scripts, projects, and experiments with
  varying levels of completeness. Existing implementations may reveal solutions.
- [Older kata catalog and ideas](README/katas/index.md): a resource, not an active queue.
- [Earlier vision](README/vision.md): preserved philosophy and platform proposals.

Only the Python exercises and Rust proof exercise are documented as
self-contained practice paths.
Keep the active scope small; use a few real sessions to decide what to add next.

## Check the CLI implementation

These integration tests use disposable practice copies, not your local answers:

```sh
cargo build --locked
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```
