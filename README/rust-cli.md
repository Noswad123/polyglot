# Rust CLI: shared practice workflow

[Home](../README.md) · [Architecture](architecture.md) · [Roadmap](../ROADMAP.md)

## Overview

This implements the shared practice workflow and a line-based session.
Python, Rust, TypeScript, Go, Bash, and Lua share prompt/hint presentation,
navigation, and check orchestration, in that native language/menu order.
The [full question/reference inventory](katas/index.md) registers 37 topic families:
five curated, 15 draft, and 17 missing questions. Its 20 documents and 74 source
artifacts across eight languages are discoverable: 60 unverified legacy files plus
14 checked examples. All five curated questions have Python and Rust bindings;
Hello World additionally has TypeScript, Go, Bash, and Lua bindings (14 total).
JavaScript and Lisp are inventory-only, with no JavaScript practice track.
Discovery adds no native adapters and never executes stored implementations.
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

## Build

Requires Rust/Cargo 1.85+ to build. Python checks require Python 3.11+; listing and
starting do not require an installed Python interpreter or exercise toolchain.
Other check requirements are Node 18+ with TypeScript 5+, Go 1.20+, Bash 3.2+,
or Lua 5.1+ (regular-file stdout flush/seek support). Install only the tools for
your chosen track. TypeScript's private package and lockfile pin 5.9.3; explicitly
run `npm ci --ignore-scripts --prefix practice/typescript` from the root. Checks
never run npm, install dependencies, or download a toolchain.

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
existing installed copy. `make install-dev` is an alias. The former Python
runtime package and `pylearn` command are removed; Python configuration is only
development/test tooling.

The install target creates the destination directory if needed, but does not
change PATH. If it is not on PATH, invoke `~/.local/bin/polyglot` directly.
Rerun `make install` after source changes; the installed binary is a copy, not a
symlink. It uses the build checkout as its default root even when run elsewhere.
Shared question Markdown is read from the selected checkout at runtime: edits on
its current branch appear without rebuilding. Static problem metadata, bindings,
and native-signature prompts require a rebuild and reinstall.

Both paths can be overridden (including paths containing spaces):

```sh
make install INSTALL_DIR="/path/to/dev/bin" TARGET_DIR="/path/to/build/cache"
```

`TARGET_DIR` defaults to `CARGO_TARGET_DIR` when set, otherwise `target`. The build
passes that directory explicitly to Cargo and installs its native debug binary.
`make build` builds without installing; plain `make` still displays help.
This is a local development install, not release packaging.

## API / Interfaces

### Questions, bindings, start, check

```sh
./target/debug/polyglot list
./target/debug/polyglot list --language python
./target/debug/polyglot list --language rust
./target/debug/polyglot questions --pretty
./target/debug/polyglot question binary-search
./target/debug/polyglot question boggle
./target/debug/polyglot question stack
./target/debug/polyglot question two-sum
./target/debug/polyglot show python/binary_search

./target/debug/polyglot practice python/hello
./target/debug/polyglot practice rust/hello
./target/debug/polyglot practice typescript/hello
./target/debug/polyglot practice go/hello
./target/debug/polyglot practice bash/hello
./target/debug/polyglot practice lua/hello
```

For one-shot selection, first create or select a non-`main` branch, then use
`start ID`, edit the displayed file, and run `check ID`. `start` will not silently
switch branches. It validates and displays an existing **Exercise file:**; it
does not copy a template or launch an editor. A missing exercise requires reset
from the committed-main baseline. Standalone `check` never initializes an attempt.

Python's track order is `python/hello`, `python/find_in_string`,
`python/length_of_last_word`, `python/binary_search`, `python/fibonacci`.
`check python` checks all five native tests; `check rust` checks all five Rust
bindings sequentially, may stop on the first non-pass, and requires all five to pass.
Python uses independent `practice/python/exercises/<ID suffix>.py` modules and
corresponding `tests/test_*.py` files. Rust uses
five independent `practice/rust/exercises/*.rs` files. Hello retains `checks.rs`
and target `practice_checks`; the other four use `tests/<exercise>.rs` and target
`<exercise>_checks`, each including only its own exercise. Selecting another
exercise does not reset your work. Track READMEs link to the authoritative shared
questions and document native APIs/commands; the CLI reads full question Markdown
and adds the selected native task. Hints remain separate static binding metadata.
TypeScript, Go, Bash, and Lua each have only `LANGUAGE/hello`; `check LANGUAGE`
selects that single binding. See their track READMEs for exact native APIs.

`questions [--json | --pretty]` inventories all 37 stable problem IDs. The default
and the retained explicit `--json` alias emit only a JSON array on stdout, with no
human header, footer, or totals. The metadata schema is unchanged: each object has `id`, `title`,
`question_status` (`curated`, `draft`, `missing`), nullable `question_doc`,
`references` (objects with `language`, `path`, nullable `note`), and `bindings`
(exercise-ID strings). Document and reference paths remain repository-relative.
Solution paths use the mixed `practice/` roots in the [inventory](katas/index.md). The legacy export key
`references` is retained for compatibility, not verification; no `solutions`
alias field is added. Internal reference metadata types remain unchanged.

`questions --pretty` selects a human-readable ASCII table, **not pretty-printed
JSON**. It fits within 80 columns and has no duplicate `Title` column:

| Column | Meaning |
|---|---|
| `Problem ID` | Stable problem ID |
| `Question` | `curated`, `draft`, or `missing` status |
| `Solutions` | Stored implementation languages (not all checked), wrapped in the same 18-character column |
| `Practice` | Runnable native languages, e.g. `python, rust`; `-` means not converted |

The footer reports 37 topics, 20 docs, 74 solution artifacts, and 14 native
bindings. Its legend
distinguishes stored implementations (not all checked) from runnable native practice and
points to JSON or `question ID` for details. Titles, exact binding IDs, and full
reference source paths remain available there rather than in the compact table.
No format flags may be mixed or repeated: `--json --pretty`, `--json --json`, and
`--pretty --pretty` are invalid (Blocked, exit `2`), as are unknown flags or extra
arguments. The selected format does not change catalog contents or native behavior.

For machine export (examples only):

```sh
polyglot questions > /tmp/polyglot-questions.json
polyglot questions --json
```

Hyphenated problem IDs are distinct from qualified exercise IDs such as
`python/binary_search`. `list`, `practice`, `start`, `check`, `reset`, `hint`, and
`show` remain restricted to the 14 active bindings (or supported track targets).
Guessing `python/stack` or `python/boggle` is blocked without writes or branch
mutation. Existing `README/katas/` filenames remain unchanged for link stability.

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

Without a target, choose a language name or menu number: `1` Python, `2` Rust,
`3` TypeScript, `4` Go, `5` Bash, `6` Lua. Quit or
EOF before selection creates no file or branch. Entering a session validates the
selected exercise and its shared document before automatic branching, preserves
existing work, and displays the exercise, position, file, problem ID, question
file, full shared Markdown, and native language task. Hints appear only when requested.

Edit and save the displayed file in your own editor. The session does not open an
editor, monitor saves, or automatically run checks.

| Session command | Behavior |
|---|---|
| Enter, `check`, `c` | Check the selected exercise; stay on it |
| `hint`, `h` | Show a hint, not a full solution |
| `prompt` | Reread and display the full shared contract plus native language task |
| `reset`, `r` | Confirm reset of only the selected exercise from committed main |
| `next`, `n` | Recheck current source; advance only if it passes |
| `previous`, `p` | Move back without requiring a pass |
| `list`, `l` | List exercises in the selected language |
| `language LANGUAGE` | Switch to the first exercise in any of the six native languages |
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

## Read a question, binding, or hint without starting

```sh
./target/debug/polyglot questions --pretty
./target/debug/polyglot question find-in-string
./target/debug/polyglot show python/find_in_string
./target/debug/polyglot hint rust/hello
```

`question PROBLEM_ID` accepts any registered topic and prints its metadata,
bindings, and stored paths under a `Solutions` heading marked “not all checked”.
Fourteen curated examples have the note “Example checked against current native tests;
not a proof of all behavior.” The original 60 legacy sources remain uncertified.
Curated topics show the full contract;
drafts show a warning and legacy body, or an empty-draft notice with success.
Missing-question topics show metadata and paths without a fabricated `Prompt:`
or an error. A declared document that is missing, unreadable, non-UTF-8,
symlinked, or a directory is Blocked (`2`), including for drafts.
It requires neither Git nor a language workspace or toolchain and performs no
writes. References are never read, imported, or executed. `show ID` displays the exercise path, `Problem:`
ID, `Question file:`, `Prompt:` containing the full shared Markdown, and
`Language task:` containing the selected native binding. Neither reveals a hint;
`hint ID` displays only the hint. These commands do not start attempts or tools.

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
list/questions/question/show/hint/check are permitted on main and do not require Git.

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
/path/to/polyglot --node "/path/to/node" --tsc "/path/to/typescript/bin/tsc" check typescript/hello
/path/to/polyglot --go "/path/to/go" check go/hello
/path/to/polyglot --bash "/path/to/bash" check bash/hello
/path/to/polyglot --lua "/path/to/lua" check lua/hello
```

Python selection is `--python` → checkout `.venv/bin/python` (or
`.venv/Scripts/python.exe`) → `python3` on PATH. The selected interpreter and
version are displayed. An explicitly selected or existing repository interpreter
that cannot run is blocked; it does not silently fall back after failure.

Cargo selection is `--cargo` → `cargo` on PATH. Paths may contain spaces; tools
are invoked as argument vectors without shell interpolation. No command installs
tools, creates environments, or downloads exercise dependencies automatically.

Node, Go, Bash, and Lua selection is the matching override (`--node`, `--go`,
`--bash`, `--lua`) → matching executable on PATH. TypeScript compiler selection is
`--tsc` → checkout `practice/typescript/node_modules/typescript/bin/tsc` if present
→ `tsc` on PATH. The compiler entry is canonicalized and must be an actual npm
`typescript/bin/tsc` with package metadata and `lib/typescript.js`, not an executable
shim (for example Volta). The selected Node runs its version probe and compiler API;
TypeScript 5+ and matching reported versions are required. Explicit/local failures
block rather than triggering installation or a silent fallback.

## Data Flow

`library.rs` provides `Problem { id, title, question_status, question_doc,
references }` and the full `PROBLEMS` registry. `question_doc` is optional;
references carry language/path/optional-note metadata, not native check selectors.
`model.rs` re-exports library types and provides the static `Exercise` catalog (ID, file, language, typed
`problem: &'static Problem`, native-signature prompt, hint, native selector).
`workflow.rs` reads the registered question document at runtime for `question`,
`show`, `start`, and sessions; it does not discover arbitrary Markdown files.
`workspace.rs` validates common inputs plus only
the selected exercise/harness. Python's `exercises/__init__.py` has no re-exports:
broken or missing unselected sibling modules/tests do not block a selected check.
For example, hello selects `tests.test_hello.PracticeTests.test_hello`.
The Python adapter launches a fresh-source helper with a separate result report;
Rust uses typed `NativeCheck::Rust(RustCheck { target, selector, harness })` data,
Cargo JSON, and the selected libtest executable. The Rust adapter builds only that
target and runs its exact selector. The manifest disables automatic libraries,
binaries, and tests (`autolib`, `autobins`, `autotests` are false); each explicit
target includes only its own exercise. Missing or broken unselected sources and
harnesses do not block selected checks. Checks do not
trust learner stdout as a pass signal. Metadata listing needs no root files, Git,
or tools. The catalog is static, not runtime file discovery or a filesystem audit;
editing Markdown does not automatically curate a draft or register a binding.

The additional Hello adapters retain native evidence and selected isolation:

- **TypeScript:** typed `NativeCheck::TypeScript { harness, config, api }` selects
  a strict compiler-API program containing just the exercise and exact `() => void`
  export probe. CommonJS output goes to private scratch, then the synchronous
  function is executed and its `undefined` return checked. A separate JSON report
  distinguishes configuration, compilation, and runtime outcomes.
- **Go:** `NativeCheck::Go { harness }` copies just `hello.go` and `hello_test.go`
  into private scratch. `go test -json -count=1 -run ^TestHello$` selects those files;
  success requires normal test-run, test-pass, and package-pass events. The child
  sets `GO111MODULE=off`, `GOWORK=off`, `GOPROXY=off`, `GOSUMDB=off`,
  `GOTOOLCHAIN=local`, `GOENV=off` and removes `GOFLAGS`. No neighboring legacy
  programs, modules, workspaces, or automatic downloads participate.
- **Bash/Lua:** native harness selectors copy only the selected source/harness into
  private scratch. Bash runs with `--noprofile --norc`; startup environment variables
  are removed, including Lua init variables. Harnesses check function availability,
  status/return arity, load-time output, and separate completion reports.

TypeScript, Bash, and Lua reject import/source/load-time stdout and compare function
output exactly with `Hello, World!\n`. File captures are backend-managed and reports
are separate from learner stdout. **Do not invoke the TypeScript or Lua harness
bare:** both require initially empty private regular-file stdout; Lua additionally
needs flush/seek support. Use `polyglot check` for the complete workflow. Go instead
checks the return from `Hello() string` in `package exercises`, without a newline.

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
- Missing, empty, unreadable/non-UTF-8, non-regular, or symlinked curated Markdown
  blocks `question`, `show`, `start`, and session entry/navigation. Draft detail
  permits empty bodies; a registered `None` document permits metadata-only detail.
  Other declared-document errors still block draft detail. Validation
  happens before automatic branching or committing a new selection. `list`,
  `questions`, `hint`, and native checks do not require question documents.
- `check` never initializes or resets an attempt. It may write normal Rust build
  artifacts, but locked checks do not update source inputs or lockfiles.
- Workspace symlinks and existing symlinks inside the isolated Rust build tree are
  rejected before native execution. This protects against existing path mistakes,
  not hostile concurrent filesystem replacement.
- Learner code runs with your privileges. This is not a sandbox for untrusted packs.
- General concept notes remain canonical in Darkness and are never loaded or
  edited by the CLI; repository questions own exercise instructions.

Direct native check commands remain in the [Python](../practice/python/README.md)
and [Rust](../practice/rust/README.md) instructions.
The [TypeScript](../practice/typescript/README.md), [Go](../practice/go/README.md),
[Bash](../practice/bash/README.md), and [Lua](../practice/lua/README.md) tracks
document setup and adapter-managed checks. Missing tools/broken harnesses block;
learner contract errors fail. Early exit without trustworthy completion evidence
is indeterminate; printing a pass marker or selecting zero/skipped tests never passes.

## Verify the implementation

```sh
cargo fmt --all -- --check
cargo test --locked
cargo clippy --locked --all-targets -- -D warnings
cargo build --locked
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

The core integration suite needs Python 3.11+ and Cargo on PATH; the additional
native Hello cases need Node/TypeScript, Go, Bash, and Lua for their respective
checks and may skip when host tools are absent. TypeScript setup is explicit, not
performed by tests or grading. The suite runs the built
`target/debug/polyglot`; set `POLYGLOT_BIN` to test a different binary. A missing
binary fails with build instructions rather than silently skipping the suite.
The fixtures are isolated temporary copies, with temporary Git repositories where
needed, paths with spaces, and unrelated working directories. Active fixture
selection and explicit solution cases live in `tests/active_fixture.py`. Fixtures
copy the curated shared Markdown. `EXAMPLE_PATHS` maps ten Python/Rust examples;
`HELLO_EXAMPLE_PATHS` maps the four additional Hello examples.
`SOLUTIONS` and `RUST_SOLUTIONS` read their actual files as text and install them
only into disposable learner sources before native checking;
tests do not copy, reset, or check real local learner answers. Retired prototype
tests are not part of the active suite or required for authoring validation.
Unix-specific symlink/shim cases are skipped on other platforms. Runtime platform
validation so far is macOS only; this is not a full test run of the unverified
collections under `practice/`. The old Python pytest files and compatibility
bridge were removed, not replaced by the active native tests. See the
[collection limits](exercises.md#collection-layout-and-execution-limits).

`tests/test_library_inventory.py` independently compares the registry with all
20 non-index question paths and 74 source artifacts (60 original legacy files plus
14 checked examples). Its filename normalization maps `hello_world` to
`hello-world`, not a variant topic. Tests/specs, manifests,
generated files, playgrounds, and the ideas backlog are not cataloged solution artifacts.
New in-scope source additions fail the coverage audit until registered; this audit
does not execute or validate legacy solutions.

`tests/test_curated_batch.py` checks the ten Python/Rust examples as disposable
learner inputs, selected Rust isolation, whole-track requirements, and independent
fixed contract cases in both languages. `tests/test_local_links.py` audits authored
Markdown targets and fragments without fetching URLs or executing examples.
`tests/test_additional_hello.py` covers the four additional blanks/examples, static
TypeScript API mutants, exact stdout/returns/status, tool versions/paths, early
exits, broken harnesses, Go offline isolation, tool-free metadata, menus, and reset
in committed disposable fixtures. Native cases require the respective installed
host tools; parent/full validation must arrange those explicitly, never by grading.

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
- [Shared question library and conversion queue](katas/index.md)
- [Collection layout and execution limits](exercises.md#collection-layout-and-execution-limits)
- [Python track](../practice/python/README.md), [Rust track](../practice/rust/README.md)
- [Full inventory](../cli/src/library.rs), [native bindings](../cli/src/model.rs),
  [inventory audit](../tests/test_library_inventory.py), [workspace validation](../cli/src/workspace.rs),
  [workflow](../cli/src/workflow.rs), [session](../cli/src/session.rs)
- [Git policy/baseline](../cli/src/git.rs), [reset](../cli/src/reset.rs),
  [native filesystem backend](../cli/src/reset/native.rs)
