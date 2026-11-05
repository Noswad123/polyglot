# Rust CLI: shared practice workflow

[Home](../README.md) · [Architecture](architecture.md) · [Roadmap](../ROADMAP.md)

This implements the Phase 2 proof and the first Phase 3 line-based session.
Python and Rust share prompt/hint presentation, navigation, and check orchestration.
It is not yet the full edit-and-save Rustlings experience: watching remains next.
The Python prototype remains available; no learner files are migrated or removed.

## Build

Requires Rust/Cargo 1.85+ to build. Python checks require Python 3.11+; listing and
starting do not require an installed Python interpreter or exercise toolchain.

From the repository root:

```sh
cargo build --locked
./target/debug/polyglot --help
```

The CLI's only direct crate dependency is `serde_json`. The first build may need
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
the older Python CLI. Use `make install-python` for that legacy tool.

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
This is a local development install, not release packaging or adoption/retirement
of the prototype.

## List, start, check

```sh
./target/debug/polyglot list
./target/debug/polyglot list --language python
./target/debug/polyglot list --language rust

./target/debug/polyglot start python/hello
# Edit practice/python/answers.py, then:
./target/debug/polyglot check python/hello

./target/debug/polyglot start rust/hello
# Edit practice/rust/answers.rs, then:
./target/debug/polyglot check rust/hello
```

The other Python IDs are `python/find_in_string` and
`python/length_of_last_word`. `check python` and `check rust` check a whole track.
Python's three exercises share one answer file; selecting another does not reset
your work. Track READMEs document the contracts; the CLI displays each exercise's
prompt and hint from its catalog metadata.

The catalog is deliberately built in. It describes exercise IDs and native check
selectors separately from workspace mappings. There is currently one workspace
per language; independent workspace metadata should be introduced when a second
workspace within one language is needed, not through a plugin framework now.

## Practice in a session

```sh
./target/debug/polyglot practice
./target/debug/polyglot practice python
./target/debug/polyglot practice rust
./target/debug/polyglot practice python/find_in_string
```

Without a target, choose `python`/`rust` or `1`/`2` at the language menu. Quit or
EOF before selection creates no answer. Entering a session safely prepares the
selected answer, preserving existing work, and displays the exercise, position,
answer path, and task. Hints appear only when requested.

Edit and save the displayed file in your own editor. The session does not open an
editor, monitor saves, or automatically run checks.

| Session command | Behavior |
|---|---|
| Enter, `check`, `c` | Check the selected exercise; stay on it |
| `hint`, `h` | Show a hint, not a full solution |
| `prompt` | Repeat the task |
| `next`, `n` | Recheck current source; advance only if it passes |
| `previous`, `p` | Move back without requiring a pass |
| `list`, `l` | List exercises in the selected language |
| `language python`, `language rust` | Switch to that language's first exercise |
| `help`, `?` | Show session commands |
| `quit`, `q`, EOF | End the session without changing answer files |

`next` does not trust an earlier pass: it checks again, including after an external
edit. At the last exercise it reports `End of track` and stays there; it does not
wrap or claim every exercise has been completed. Preparation must succeed before
navigation changes the selection. Switching languages preserves both answer files.

Failed, blocked, and indeterminate checks leave the session usable. Clean quit/EOF
returns `0` because the session ended normally, **not** because the exercises all
passed. Use one-shot `check` for a machine-readable check exit code.

There is no saved selection or progress; a new session starts at its requested
target or language menu. Edits during an active native process are not yet tracked
or used to invalidate that running result; superseded-run handling belongs to the
watch increment. For now, finish editing and save before requesting a check.

## Read a prompt or hint without starting

```sh
./target/debug/polyglot show python/find_in_string
./target/debug/polyglot hint rust/hello
```

These commands do not create attempts or launch language tools. `show` displays
the task and answer path without revealing the hint; `hint` displays only the hint.

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

## Outcomes and safety

| Exit code | Meaning |
|---|---|
| `0` | The selected checks actually ran and passed |
| `1` | An attributable learner-code or assertion failure |
| `2` | Invalid input or a blocked check: missing tools, bad target/configuration |
| `3` | Interrupted or indeterminate: no trustworthy normal result |

Native diagnostics are preserved. Ambiguous errors are not automatically blamed
on the learner. Zero selected tests and ignored/skipped checks do not pass.
Python uses fresh source and a separate result report rather than trusting learner
stdout; Rust uses Cargo compiler messages and the selected native test executable.
Rust outcome detection relies on Cargo JSON and stable libtest inventory/result
text, not a universal diagnostic parser.

- `start` exclusively creates an absent answer and preserves an existing one.
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
python3 -B -m unittest discover -s tests -p test_rust_cli.py -v
python3 -B -m unittest discover -s tests -p test_interactive_cli.py -v
python3 -B -m unittest discover -s tests -p test_polyglot_cli.py -v
```

The integration suite needs Python 3.11+ and Cargo on PATH. It runs the built
`target/debug/polyglot`; set `POLYGLOT_BIN` to test a different binary. A missing
binary fails with build instructions rather than silently skipping the suite.
The fixtures are disposable copies in temporary directories, including paths with
spaces and an unrelated working directory. Real local answers are never copied,
reset, or checked by these tests. Unix-specific symlink/shim cases are skipped on
other platforms; the current proof was exercised on macOS.

## Not implemented yet

No watch mode, persistent progress, automatic reset, editor launching, TUI, or
release distribution. The local debug install above is supported. No Rustlings
code was copied for these slices.
Next comes watching and superseded-run handling; the Python prototype is retired
only after later adoption checks.
