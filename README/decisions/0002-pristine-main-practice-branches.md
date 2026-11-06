# ADR 0002: Pristine main and practice branches

**Status:** Accepted; branch safeguards and an opt-in commit hook are implemented.
Migration to tracked per-exercise files and reset are not implemented yet.

[Architecture](../architecture.md) · [Roadmap](../../ROADMAP.md)

## Decision

`main` contains the canonical blank exercises. Learners edit and may commit their
attempts on a separate branch. Curriculum changes also use an authoring branch;
practice solutions should not be merged back into `main`.

Use Git to separate pristine material from practice, rather than maintaining a
learner-facing starters/answers pair. The target layout is one tracked
`practice/<language>/exercises/` directory, with independent modules and tests.
That layout migration follows this branch-safety increment; current ignored
`answers.py`/`answers.rs` files are preserved, not silently converted or discarded.

## Rust CLI policy

- `practice` reuses a committed named branch other than `main`, including one with
  uncommitted work.
- On clean `main`, it creates a unique `practice/<language>-...` branch from the
  current commit before preparing an attempt. It never switches to an existing
  branch automatically or moves the `main` ref.
- On dirty `main`, it refuses automatic creation. The learner can explicitly use
  `git switch -c practice/my-session` to carry work to a new branch, or make main
  clean first. The tool never stashes, resets, commits, fetches, or forces a switch.
- `start` requires a non-`main` branch and does not create one automatically.
- Practice/start require an exact top-level Git checkout or linked worktree with a
  committed, named HEAD. Detached, unborn, bare, nested-root, and non-repository
  contexts are blocked rather than inferred or initialized.
- Initial workspace conflicts are checked before automatic branch creation.
- Session checks and navigation revalidate branch safety. An external switch to
  `main` blocks those actions; it does not silently create another branch.
- Menu quit/EOF before selection makes no branch or answer changes.

Standalone list/show/hint/check remain usable on `main` and without Git. One-shot
checking is useful for validating canonical material; it does not prepare answers.
Native tools may still produce their usual build artifacts.

Only Rust CLI commands enforce this policy. The retained Python prototype and
direct native/editor commands do not acquire a Git guard automatically.

## Protecting direct commits

An optional `.githooks/pre-commit` guard rejects staged exercise changes on `main`.
It covers the target `practice/*/exercises/**` tree plus the transitional Python
and Rust starter/answer files, including deletions and renames out of protected
paths. It does not reject unrelated staged documentation or tooling changes.

Activate it explicitly with `make install-hooks`. Installation creates an
executable hook in Git's default hook directory without changing Git config.
Existing different hooks, symlinks, or a configured `core.hooksPath` are not
overwritten; integrate the guard with that setup manually. It is not installed by
`make install` or by entering practice. Linked worktrees may share the hook directory.

## Enforcement limits

Git branches and hooks do not make editor buffers or working-tree files read-only.
The CLI guards its own preparation and practice operations; the hook guards direct
commits only after installation. Local hooks are bypassable and are not a security
boundary. Remote branch rules and review policies are a separate owner-managed
layer; no remote settings are changed by this implementation.

The guard does not semantically prove that an exercise is blank. Changes to
canonical exercises require review on an authoring branch before integration.

## Reset and migration follow-up

Before watch mode, replace the shared answer files with independent tracked
exercise modules while preserving existing learner implementations separately.
Do not use a learner branch's HEAD as a pristine reset source. A future reset must
resolve an explicit canonical revision of `main`, back up the selected file,
confirm replacement, and restore only that exercise without altering the index
or unrelated files. The exact baseline/version policy is part of that next gate.

No reset command, automatic migration, or new progress store is introduced here.
