# ADR 0002: Pristine main and practice branches

**Status:** Accepted; branch safeguards, an opt-in commit hook, independent tracked
exercise files, and explicit reset are implemented. Ignored legacy learner answers
are preserved if present, not automatically migrated or committed. The root Python
prototype and obsolete practice starters/tests are retired.

[Architecture](../architecture.md) · [Roadmap](../../ROADMAP.md)

## Decision

`main` contains the canonical blank exercises. Learners edit and may commit their
attempts on a separate branch. Curriculum changes also use an authoring branch;
practice solutions should not be merged back into `main`.

Use Git to separate pristine material from practice, rather than maintaining a
learner-facing starters/answers pair. The active layout is one tracked
`practice/<language>/exercises/` directory, with independent modules and tests.
Current ignored `answers.py`/`answers.rs` files are preserved, not silently
converted or discarded, and are not imported by the Rust CLI.

The separate [repository inventory](../katas/index.md) maps preserved implementations
under mixed `practice/` roots, not converted into learner blanks. This layout does
not migrate or delete personal answers, expand hook protection to inventory
sources, or create reset baselines.
Question documents remain in `README/katas/`.

## Rust CLI policy

- `practice` reuses a committed named branch other than `main`, including one with
  uncommitted work.
- On clean `main`, it creates a unique `practice/<language>-...` branch from the
  current commit before preparing an attempt. It never switches to an existing
  branch automatically or moves the `main` ref.
- On dirty `main`, it refuses automatic creation. The learner can explicitly use
  `git switch -c practice/my-session` to carry work to a new branch, or make main
  clean first. The branch policy never stashes, restores files, commits, fetches,
  or forces a switch. Only the separate explicit reset command restores an exercise.
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

Only the shared Rust CLI enforces this policy. `polyglot` is the only supported
practice CLI; direct native/editor commands do not acquire a Git guard automatically.

## Protecting direct commits

An optional `.githooks/pre-commit` guard rejects staged exercise changes on `main`.
It covers `practice/*/exercises/**`, `practice/python/answers.py`, and
`practice/rust/answers.rs`, including deletions and renames out of protected paths.
Retired starter paths are not protected. It does not reject unrelated staged
documentation or tooling changes.

Activate it explicitly with `make install-hooks`. Installation creates an
executable hook in Git's default hook directory without changing Git config.
Existing different hooks, symlinks, or a configured `core.hooksPath` are not
overwritten; integrate the guard with that setup manually. It is not installed by
`make install` or by entering practice. Linked worktrees may share the hook directory.
Updating the tracked guard does not update an already-installed older hook; it is
a different existing hook and the installer refuses to replace it. Integrate guard
changes manually with the existing setup.

## Enforcement limits

Git branches and hooks do not make editor buffers or working-tree files read-only.
The CLI guards its own preparation and practice operations; the hook guards direct
commits only after installation. Local hooks are bypassable and are not a security
boundary. Remote branch rules and review policies are a separate owner-managed
layer; no remote settings are changed by this implementation.

The guard does not semantically prove that an exercise is blank. Changes to
canonical exercises require review on an authoring branch before integration.

## Canonical reset and legacy preservation

`reset ID` and session `reset`/`r` require a non-main branch and accept only one
explicit exercise. Resolve `refs/heads/main` to a full commit once per operation,
then read that commit's exact regular-file blob. Disable Git object replacements;
never use learner HEAD, working-tree contents, or a legacy starter as fallback.
The latest reviewed local main is the baseline at reset start, not a permanently
recorded practice-branch creation revision. A later main-ref change during the
confirmation does not substitute another blob into that operation.

The canonical file must already be committed at its exercise path on local main.
Catalog registration or an uncommitted blank is not a baseline. Newly
authored files need reviewed integration into main; without that baseline
reset blocks. Uncommitted cleanup on main still blocks automatic practice-branch
creation until the user explicitly branches or reconciles changes. Existing
pristine files require no write or backup. Other cases require `y`/`yes`;
cancellation/EOF returns `0` and writes nothing.

Restore only the selected worktree file, leaving the index and staged content
unchanged. On macOS/Linux, safe directory-relative operations, atomic no-replace
or exchange, private snapshot backups, and lasting original-inode recovery retain
learner bytes. A late edit can yield a blocked result after the baseline was
installed; diagnostics must explicitly identify that state and retained recovery.
Other platforms/unsupported primitives block without an overwrite fallback.
Snapshot files use `0600` and new private directories `0700`. Preserve both printed
`Backup:` and `Recovery:` paths, including any private adjacent recovery artifact
when a safe cross-filesystem move is unavailable. macOS has runtime coverage; Linux
has not been runtime-tested. Finish editing and save before checking/resetting,
and do not edit during either operation. Manual checks are intentional; no
auto-run on save or watch mode is planned.

No shared answer file is automatically parsed or deleted. Move selected functions
and needed imports manually on a practice branch, verify the checks, and preserve
the old file until satisfied. See the [exercise lifecycle guide](../exercises.md).
There is no automatic backup cleanup or new progress store.
