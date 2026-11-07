# Exercise lifecycle and authoring

[Home](../README.md) · [Shared CLI](rust-cli.md) · [Branch policy ADR](decisions/0002-pristine-main-practice-branches.md)

## Overview

Canonical blank exercises live in tracked `practice/<language>/exercises/` files.
Learners edit those same files on practice branches; `main` remains pristine.
There is no separate `starters/` directory or active shared answers file. This is
a small learning workflow, not a general exercise-pack platform.

The [shared question library](katas/index.md) owns exercise instructions and
common contracts. One question can have many native language bindings; general
concept notes remain canonical in Darkness. All 37 topic families are discoverable:
five curated contracts, 15 drafts/project sketches, and 17 code-only topics needing
questions. Fourteen bindings are active practice: all five curated questions in Python
and Rust, plus Hello in TypeScript, Go, Bash, and Lua. Stored sources mix 60
unverified legacy implementations and 14 examples
checked against current native tests, not proven for all behavior. The preserved
ideas backlog is separate. Existing `README/katas/` paths
remain stable to avoid breaking links. JavaScript and Lisp remain inventory-only;
there is no JavaScript practice track or migration of original code into blanks.

**Baseline prerequisite:** a reviewed canonical blank must be committed to local
`refs/heads/main` before reset can restore it. New or uncommitted exercise paths
are not a baseline. Until that commit exists, reset blocks safely; it does not
invent a blank or use the working tree, learner HEAD, or old starter. No automatic
commit or learner-solution migration is implied.

## API / Interfaces

| Exercise ID | Shared question / problem ID | Active file | Native selector |
|---|---|---|---|
| `python/hello` | [hello-world](katas/hello_world.md) | `practice/python/exercises/hello.py` | `tests.test_hello.PracticeTests.test_hello` |
| `python/find_in_string` | [find-in-string](katas/find_in_string.md) | `practice/python/exercises/find_in_string.py` | `tests.test_find_in_string.PracticeTests.test_find_in_string` |
| `python/length_of_last_word` | [length-of-last-word](katas/lengthOfLastWord.md) | `practice/python/exercises/length_of_last_word.py` | `tests.test_length_of_last_word.PracticeTests.test_length_of_last_word` |
| `python/binary_search` | [binary-search](katas/binarySearch.md) | `practice/python/exercises/binary_search.py` | `tests.test_binary_search.PracticeTests.test_binary_search` |
| `python/fibonacci` | [fibonacci](katas/fibonacci.md) | `practice/python/exercises/fibonacci.py` | `tests.test_fibonacci.PracticeTests.test_fibonacci` |
| `rust/hello` | [hello-world](katas/hello_world.md) | `practice/rust/exercises/hello.rs` | `hello` in `practice_checks` |
| `rust/find_in_string` | [find-in-string](katas/find_in_string.md) | `practice/rust/exercises/find_in_string.rs` | `find_in_string` in `find_in_string_checks` |
| `rust/length_of_last_word` | [length-of-last-word](katas/lengthOfLastWord.md) | `practice/rust/exercises/length_of_last_word.rs` | `length_of_last_word` in `length_of_last_word_checks` |
| `rust/binary_search` | [binary-search](katas/binarySearch.md) | `practice/rust/exercises/binary_search.rs` | `binary_search` in `binary_search_checks` |
| `rust/fibonacci` | [fibonacci](katas/fibonacci.md) | `practice/rust/exercises/fibonacci.rs` | `fibonacci` in `fibonacci_checks` |
| `typescript/hello` | [hello-world](katas/hello_world.md) | `practice/typescript/exercises/hello.ts` | `tests/check_hello.cjs`, config + static API probe |
| `go/hello` | [hello-world](katas/hello_world.md) | `practice/go/exercises/hello.go` | `TestHello` in `tests/hello_test.go` |
| `bash/hello` | [hello-world](katas/hello_world.md) | `practice/bash/exercises/hello.sh` | `tests/check_hello.sh` |
| `lua/hello` | [hello-world](katas/hello_world.md) | `practice/lua/exercises/hello.lua` | `tests/check_hello.lua` |

`cli/src/library.rs` declares `Problem { id, title, question_status, question_doc,
references }` and the full `PROBLEMS` registry. Documents are optional; references
carry language, path, and an optional note. `cli/src/model.rs` declares native
bindings. Each `Exercise` has a qualified `id`, workspace-relative
`file`, `language`, typed `problem: &'static Problem`, native-signature `prompt`,
`hint`, and `check` (`NativeCheck` selector). Rust uses
`NativeCheck::Rust(RustCheck { target, selector, harness })`: the Cargo target,
exact libtest selector, and workspace-relative harness path. The typed `problem`
reference links to the authoritative shared contract, not duplicated question text.
Native language order is Python, Rust, TypeScript, Go, Bash, Lua. TypeScript's
selector carries `harness`, `config`, and `api`; Go/Bash/Lua selectors carry their
native `harness`. Tool overrides are `--python`, `--cargo`, `--node`, `--tsc`,
`--go`, `--bash`, and `--lua`, alongside `--root`, all before the command.
Common titles/contracts are not
repeated in each binding. Stable problem IDs use hyphens, e.g. `binary-search`;
qualified exercise IDs retain native underscores, e.g. `python/binary_search`.
Adding a file alone does not register a question or binding. Ordinary exercises
need catalog/test changes, not a new adapter branch.

## Data Flow

1. Read a question with `question PROBLEM_ID`, or use `show ID` for the full shared
   Markdown plus the native language task. `questions --pretty` lists all registered
   topics in an 80-column ASCII table: problem ID, question status, wrapped `Solutions`
   languages, and runnable practice languages (`-` means not converted), with
   totals/topic counts and a legend. It is not pretty-printed JSON. `questions`
   defaults to JSON-only metadata on stdout; `--json` remains an explicit alias,
   with no human header/footer and the same schema. The legacy `references` key
   retains language/path/nullable-note entries; paths use the mixed `practice/` roots below.
   No `solutions` alias is added; this is compatibility metadata, not verification.
   Use JSON or `question ID` for titles, exact binding IDs, and full solution paths.
   Mixed or repeated format flags are rejected. Neither format is runtime file discovery.
2. `practice` validates the selection, shared document, and native workspace before
   automatic branching, then creates a unique practice branch from
   clean main, or reuses a non-main branch. Dirty main is refused without stash.
3. `start ID` validates the shared document and existing selected file and displays
   **Exercise file:**. It requires a non-main branch, copies no template, and
   launches no editor.
4. Finish editing and save the selected module, then explicitly check it with
   Enter/`check`/`c` in the session or a one-shot check. Manual checks are intentional;
   saves never trigger checks. Python tests import only their own
   exercise and shared feedback; `exercises/__init__.py` has no re-exports.
   Broken/missing unselected siblings do not prevent selected checks. Rust
   `checks.rs` calls `greeting()` from `exercises/hello.rs`; each of the other four
   `tests/<exercise>.rs` harnesses includes only its own exercise. The Rust adapter
   builds only the selected explicit Cargo target. Track checks require all five
   to pass, run sequentially, and may stop on the first non-pass.
   The four additional tracks each check only Hello. TypeScript performs real
   static API checking and runtime execution; Go uses isolated offline test JSON;
   TypeScript/Bash/Lua use separate reports and backend-managed file stdout capture.
   They reject load-time output and compare exact newline bytes. Do not invoke the
   TypeScript or Lua harness bare; private regular-file stdout is required. See
   their track READMEs for setup, tools, and contracts.
5. Retry explicitly with `reset ID` or session `reset`/`r`, after the baseline
   prerequisite above. Only that worktree file is restored; the index is unchanged.

Standalone checks and read-only commands are allowed on main. Native commands and
editors do not enforce branch policy; select a practice branch yourself. The root
Python prototype is retired; `polyglot` is the only supported practice CLI.
The optional `make install-hooks` staged-path guard covers protected
active source additions, modifications, deletions, and renames on main. It is not
an editor read-only lock, does not change remote protection, and installs no Git
configuration. It also protects the two legacy ignored answer paths, not retired
starter paths. It refuses different existing hooks or configured hook systems;
updating its tracked source does not update an already-installed older hook.
Reset never changes Git configuration, history, or the index.

## Edge Cases

Active binding display/start/session selection requires a curated, nonempty UTF-8
regular question file without symlink components; validation precedes branching
or navigation changes. `question ID` also supports drafts (warning plus legacy
body; empty drafts succeed with a notice) and missing questions (`None`: metadata
and reference paths only, no fabricated prompt). Declared missing, unreadable,
non-UTF-8, non-regular, or symlinked documents still block detail with exit `2`.
`question` needs no Git, language workspace, tools, or writes, and never reads,
imports, or executes reference sources. Metadata listing needs no root files.
`list`, `questions`, `hint`, and native checks do not require question documents.
Current-checkout Markdown edits are read at runtime without rebuilding; changes
to static problem metadata, native signatures, or bindings need build/install.

Shared string conformance covers printable ASCII plus the six standard ASCII
whitespace characters: SPACE, TAB, LF, CR, VT (`\v`/`\x0b`), and FF (`\f`/`\x0c`).
Other Unicode/control separators are not cross-language guaranteed. Python's
`str.split()` and Rust's `split_whitespace` naturally support more; Rust's
`split_ascii_whitespace` does not include VT and is not equivalent to this contract.
A new Unicode binding must explicitly
agree on index/count units and whitespace rules, not equate code points, UTF-16
units, and grapheme clusters. Keep intentional API differences explicit, including
Python Hello's printing/`None` versus Rust Hello's returned text.

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
not edit while either runs. No watch mode or auto-run on save is planned. Checks do
not automatically advance or persist progress; `next` rechecks before advancing.

## Example usage

With the shared CLI installed, from a clean canonical main:

```sh
polyglot questions --pretty
polyglot question binary-search
polyglot show python/binary_search
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

The root Python prototype and obsolete Python/Rust starter and shared test files
are retired. Ignored `practice/python/answers.py` and `practice/rust/answers.rs`
are preserved if present; they are not required to exist. The CLI never imports
or uses them, and their ignore and optional hook protection remain. No solution
from those personal answer files has been automatically copied or claimed migrated.
The preserved repository implementations under `practice/` do not import learner
answers into active exercises.

To reuse your own older solution, first select a practice branch. Manually copy
only the selected function and its needed imports into the corresponding active
exercise module; do not copy the whole old shared answers file or overwrite sibling
exercises. Save, run the selected check, and explicitly verify the saved contents
and any separate preservation copy. Keep the old file until that verification is
complete; ignored files are not protected by Git commits. Do not merge learning
solutions into main.

### Author a new exercise

1. From clean main, create an authoring branch, not a learning-solution merge.
2. Review existing question drafts and unverified inventory attempts without
   overwriting them. Define the common contract, examples, domain, edge cases, and
   explicit binding differences in the shared question document. Register its
   stable `Problem`, `question_status`, optional `question_doc`, and references in
   `cli/src/library.rs` first (or promote/reuse an existing problem); keep established
   document paths stable. Explicitly promote a reviewed contract to `Curated` before
   binding it: Markdown edits alone never change status. A curated problem need not
    have a binding. Reference-language labels do not extend the six-variant native
   `Language` enum or add an adapter.
3. Add an `Exercise` in `cli/src/model.rs` referencing that problem, with a qualified ID, file, language,
   native-signature-only prompt, hint, and native selector. Do not duplicate the
   common title or full prompt in the binding. Add a canonical blank module under
   the tracked `exercises/` path and an independent native test harness. Python
   blanks raise `NotImplementedError`; Rust blanks use `todo!()`. Keep package initializers free of sibling
   re-exports. For Rust add a separate explicit Cargo test target with its own
    harness and `RustCheck { target, selector, harness }`; do not aggregate exercises
    into one target. Keep automatic libraries/binaries/tests disabled to preserve
    selected isolation. Reuse the existing adapter, not workflow language branches.
    Rust harnesses bind the required API through a typed `const FUNCTION` assignment
    tagged `// polyglot:api` and call that pointer. Keep this marker only on the
    interface assignment: the adapter uses its primary compiler span to distinguish
    learner signature/name/visibility errors from broken harness configuration.
4. In isolated fixtures, verify the blank fails for the intended reason and a
   valid implementation passes. Check selected isolation, including broken/missing
   siblings where applicable. Update `tests/active_fixture.py`'s `QUESTIONS`,
   explicit copy selection, IDs, `EXAMPLE_PATHS`, `SOLUTIONS`, and `RUST_SOLUTIONS`
   as applicable: fixtures must copy shared Markdown as well as native inputs.
    `HELLO_EXAMPLE_PATHS` covers the four additional Hello examples.
    All 14 published examples are read as text, then copied into disposable
   learner sources. Expected native outputs are fixed independently of examples;
   never use personal learner files as fixtures or overwrite their attempts.
5. Run the [active regression commands](rust-cli.md#verify-the-implementation)
   against disposable fixtures, including question discovery/full-Markdown reads,
    binding display, and blocked-document behavior. Keep examples in solution areas
    or fixture inputs, never in canonical blank modules. Update track links and library readiness only
   after the contract, binding, blank, checks, and fixtures are in place.
   `tests/test_library_inventory.py` independently audits all 20 non-index question
    paths and 74 source artifacts (60 original legacy files plus 14 examples);
   register new in-scope sources or the audit
   fails. It excludes tests/specs, manifests, generated files, playgrounds, and the
   ideas backlog, and never validates legacy solutions. Draft discovery is not
   practice readiness; stored-solution validation is separate from a native binding,
   a committed reset baseline, and user progress. Normalize filename aliases such
   as `hello_world` to `hello-world`, not a new variant topic.
   Keep authored Markdown targets and fragments valid: `tests/test_local_links.py`
   audits the documentation corpus without running examples. Preserve established
   anchors when reorganizing existing sections.
6. Submit for PR review. The reviewed canonical blank must reach local main's
   committed tree before it becomes a reset baseline. Never merge learning
   solutions into main.

No Rustlings code has been copied. Upstream version pinning becomes relevant only
if upstream code is copied; a learning-workflow resemblance alone requires none.

### Collection layout and execution limits

The [inventory](katas/index.md) links all 74 source artifacts across 37 topics:
the original 60 legacy files plus 14 checked examples.
Their roots are intentionally mixed; preserve existing names and subdirectories:

| Collection | Repository-relative root |
|---|---|
| Python attempts | `practice/python/soutions/` (existing spelling) |
| Checked Python examples | `practice/python/soutions/curated/` |
| Checked Rust examples | `practice/rust/solutions/curated/` |
| Checked TypeScript/Go/Bash/Lua Hello examples | `practice/<language>/solutions/curated/` |
| Rust Users project | `practice/rust/solutions/users/` (including `src/main.rs`) |
| TypeScript, JavaScript, Go, Bash, Lua, Lisp | `practice/<language>/` (Go Users retains `users/`) |

Python/Rust curated directories contain one example per curated question;
TypeScript/Go/Bash/Lua each contain only Hello. These include `hello_world.py` and
`hello_world.rs` (the Rust function is `greeting`).
Their metadata notes say “Example checked against current native tests; not a proof
of all behavior.” Browsing never executes them. Legacy attempts remain unverified
and unchanged, not additional native bindings. TypeScript specs
retain their own harness expectations; Chai/Mocha dependencies and execution are
not verified here. Rust Users is a standalone isolated Cargo workspace, not the
active Rust exercise package. HTTP examples may bind ports; Users examples may
create or change databases and handle credentials. Inspect source and dependencies
before running them; do not use them to validate the 14 native bindings. The private
TypeScript 5.9.3 package supports the new Hello check only; it does not repair the
legacy Chai/Mocha specs. Install explicitly with
`npm ci --ignore-scripts --prefix practice/typescript`; graders never auto-install.

The seven old Python pytest files and compatibility import bridge were removed,
not moved into the active unittest track. They are not available validation.
The former Python package, scripts, playgrounds, frontend, and backend code were
also removed. Root `pyproject.toml` is virtual development/test configuration,
not a Python runtime distribution; any retained `pylearn` name is historical
metadata. Root tests live in `tests/`; native Python tests remain in
`practice/python/tests/`. Historical legacy test results do not validate this tree.

## Related files

- [Python contracts/native commands](../practice/python/README.md)
- [Rust contract/native command](../practice/rust/README.md)
- Hello-only tracks: [TypeScript](../practice/typescript/README.md),
  [Go](../practice/go/README.md), [Bash](../practice/bash/README.md), [Lua](../practice/lua/README.md)
- [Shared question library and conversion queue](katas/index.md)
- [Preserved source inventory](katas/index.md#solutions-for-documented-topics-unverified)
- [Full inventory/types](../cli/src/library.rs), [native bindings](../cli/src/model.rs),
  [inventory audit](../tests/test_library_inventory.py), [validation](../cli/src/workspace.rs)
- [Reset](../cli/src/reset.rs), [native backend](../cli/src/reset/native.rs), [Git baseline](../cli/src/git.rs)
- [Fixture copying/solutions](../tests/active_fixture.py), [CLI/session guide](rust-cli.md)
