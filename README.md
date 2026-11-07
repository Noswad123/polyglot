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
for Python, Rust, TypeScript, Go, Bash, and Lua through native adapters, plus a line-based practice
session with prompts, hints, navigation, and per-exercise reset from committed
`main`. All six languages use tracked `exercises/` files instead of an active
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
another checkout. There is no Python runtime package or `pylearn` entry point.

## Shared question library

The [full collection inventory](README/katas/index.md) includes **37 topic
families**, not just the five curated questions. Nothing outside that small
curated batch has been converted into a practice track. A curated problem defines
the behavior once; each language binding supplies
its native signature, blank file, hint, and tests. These are exercise contracts,
not duplicate concept notes—general explanations still belong in Darkness.

```sh
polyglot questions --pretty
polyglot question binary-search
polyglot question boggle
polyglot question stack
polyglot question two-sum
polyglot show python/binary_search
```

For machine export, `polyglot questions` emits only JSON on stdout;
`polyglot questions --json` is an explicit alias. For example:

```sh
polyglot questions > /tmp/polyglot-questions.json
```

`--pretty` means a human-readable ASCII table, not pretty-printed JSON. Its
`Problem ID`, `Question` (status), `Solutions` (wrapped language list), and
`Practice` (runnable languages, e.g. `python, rust`; `-` means not converted)
columns fit within 80 columns without a duplicate title column. The footer gives
aggregate totals (including 74 solution artifacts) and a “not all checked” legend
distinguishing stored implementations from native practice. Use JSON or `question ID` for titles, exact binding IDs, and
full solution paths. Choose at most one format flag; mixing or repeating flags
is rejected. Default/`--json` output has no human header or footer.

The `Solutions` column retains its 18-character width; its languages include both
legacy inventory and checked examples, while `Practice` lists runnable native languages. Detail output uses a
`Solutions` heading. JSON intentionally keeps the legacy `references` key and its
`language`/`path`/nullable `note` entries, with paths now under
the mixed `practice/` collection roots listed in the inventory; no `solutions` alias field is added. The legacy export
key is not a verification claim.

`show` and the practice session read the shared Markdown at runtime, followed by
the selected language task. Question edits are visible without rebuilding; catalog
or native binding changes still require a build/install. Native checks do not
depend on question-file availability.

The inventory registers five curated contracts, 15 drafts/project sketches, and
17 topics still needing question documents: 20 existing documents and 74 source
artifacts across eight languages under `practice/`: the original 60 unverified legacy
implementations plus 14 checked examples (five Python, five Rust, and one Hello
each in TypeScript, Go, Bash, and Lua). Each new example
has a metadata note: “Example checked against current native tests; not a proof of
all behavior.” Discovery never reads or executes these sources.
`questions` lists all 37 topics; `question ID` also accepts drafts and code-only
topics. `list` and practice commands expose 14 active bindings: all five curated
questions in both Python and Rust, plus Hello World in TypeScript, Go, Bash, and Lua.
Native language/menu order is Python, Rust, TypeScript, Go, Bash, Lua. JavaScript
and Lisp are inventory-only; there is no JavaScript practice track. Solution-language
labels do not add native adapters. Metadata discovery is read-only and tool-free.
Use the curated contract when porting a question.

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

The active files are under `practice/<language>/exercises/` for all six native
languages. Current ignored legacy answer files are
preserved if present, not automatically split or imported. The optional guard
covers active `practice/*/exercises/**` paths and the two legacy answer paths,
not retired starter paths. Editor and native commands do not enforce branch safety.

On a practice branch, `polyglot reset python/hello` (or session `reset`/`r`) asks
before restoring only that exercise from a pinned commit of local `main`.
Any newly added binding becomes reset-ready only after its reviewed blank is
committed at its path on local `main`; a working-tree file is not enough. Reset
readiness is a committed-tree prerequisite, not implied by catalog registration.
Uncommitted changes on main still block automatic
practice-branch creation until you explicitly branch or reconcile them.
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
resolves native tools explicitly; see `--python`, `--cargo`, `--node`, `--tsc`,
`--go`, `--bash`, `--lua`, and `--root` in its instructions. Options precede commands.

Direct native commands remain in the track instructions; use them on a practice
branch too. They do not enforce the CLI's branch safeguards.

Python and Rust cover the same five questions, a small practice path rather than a full curriculum:

1. **Hello World:** functions and observable output; skip quickly if familiar.
2. **Find in String:** return values and text searches.
3. **Length of Last Word:** text cleanup and edge cases.
4. **Binary Search:** sorted search, boundaries, and boolean results.
5. **Fibonacci:** exact sequence length and recurrence.

The four additional tracks are Hello-only: [TypeScript](practice/typescript/README.md)
(Node 18+, TypeScript 5+), [Go](practice/go/README.md) (1.20+),
[Bash](practice/bash/README.md) (3.2+), and [Lua](practice/lua/README.md) (5.1+).
TypeScript's private package/lock pins 5.9.3; explicitly install from the root with
`npm ci --ignore-scripts --prefix practice/typescript`. Grading never auto-installs.
TypeScript checks the real static exported synchronous `hello(): void` API, exact
newline output, and `undefined` return. Go returns the greeting without a newline
from `Hello() string` in `package exercises`. Bash requires exact newline stdout
and status 0; Lua requires exact newline stdout and no values or a single `nil`.
TypeScript/Bash/Lua reject load-time output and use separate reports with
backend-managed file capture. Follow the CLI workflow rather than invoking the
TypeScript or Lua harness bare.

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
- **Retired platform experiments:** the older `pylearn` package, scripts,
  playgrounds, frontend, and backend code have been removed, not relocated.
  Root Python configuration is development/test tooling, not a runtime package;
  a historical `pylearn` metadata name does not provide a command or import.

## Find your way around

- [Roadmap](ROADMAP.md): boundaries, phased work, acceptance criteria, and deferrals.
- [Target architecture](README/architecture.md): Darkness as knowledge, Polyglot as
  practice, and a shared Rust workflow with native adapters as the target.
- [Architecture decision](README/decisions/0001-shared-workflow-language-adapters.md):
  adapter boundaries, outcome semantics, and adoption status.
- [Pristine-main decision](README/decisions/0002-pristine-main-practice-branches.md):
  branch creation, direct-commit safeguards, and migration limits.
- [Shared Rust CLI](README/rust-cli.md): build/run instructions for all six native languages,
  tool selection, safety, and outcome codes.
- [Exercise lifecycle and authoring](README/exercises.md): tracked files, safe reset,
  preserving older attempts, and creating or fixing exercises.
- [Python exercises](practice/python/README.md): prompts, checks, and retry instructions.
- [Rust exercises](practice/rust/README.md): five isolated native Cargo check targets.
- [Solutions inventory](README/katas/index.md): preserved implementations and attempts across eight
  languages, with their support files; mixed legacy inventory and checked examples,
  potentially revealing answers.
- [Full question/solution inventory](README/katas/index.md): all 37 topic families,
  curated bindings, draft and code-only queues, and the original ideas/resources
  backlog—not today's assignment list.
- [Earlier vision](README/vision.md): preserved philosophy and platform proposals.

Python and Rust have five-question paths; TypeScript, Go, Bash, and Lua have
bounded Hello-only paths. No original inventory code is migrated into exercises.
Keep the active scope small; use a few real sessions to decide what to add next.

## Check the CLI implementation

These integration tests use disposable practice copies, not your local answers:

```sh
cargo build --locked
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

The fixtures read published curated examples as text and copy them into disposable
learner sources; they never overwrite your attempts. Passing native checks is
evidence for those cases, not proof of all behavior or recorded user progress.
