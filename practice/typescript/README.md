# TypeScript practice track

[Home](../../README.md) · [Shared CLI](../../README/rust-cli.md) · [Exercise lifecycle](../../README/exercises.md)

## Overview

One active binding, `typescript/hello`, uses the shared
[Hello World contract](../../README/katas/hello_world.md). The other TypeScript
sources and specs remain legacy inventory, not converted exercises. Use Node 18+
and TypeScript 5+ with a working compiler API. The private package and lockfile
pin TypeScript **5.9.3**. From the repository root, install explicitly:

```sh
npm ci --ignore-scripts --prefix practice/typescript
```

Grading never runs npm or installs dependencies. Missing tools block checking;
metadata commands (`list`, `questions`, `question`, `show`, `hint`) need no native tools.

## API / Interfaces

Implement `export function hello(): void` in [exercises/hello.ts](exercises/hello.ts).
It must synchronously print exactly `Hello, World!` plus one newline and return
`undefined`. The named export's static type must be exactly `() => void`;
async functions, required arguments, `any`, and default-only exports do not satisfy
the API probe. Do not print at module load time.

Tool selection is `--node PATH` then `node` on PATH. Compiler selection is
`--tsc PATH` → checkout `practice/typescript/node_modules/typescript/bin/tsc`,
if present → `tsc` on PATH. The selected entry is canonicalized and must be the
actual npm `typescript/bin/tsc` with its package metadata and sibling
`lib/typescript.js`, not a Volta or other executable shim. Node runs both the
entry's version probe and the matching compiler API; their versions must agree.
Global overrides, including `--root`, precede the command.

## Data Flow

The adapter validates the harness and compiles only the selected exercise and
[API probe](tests/hello_api.ts) using [the strict config](tests/hello.tsconfig.json).
It performs real static checking, not transpile-only execution. Emitted CommonJS
and its package marker live in private temporary scratch; unrelated legacy specs
are not selected. The runtime harness rejects import-time output, calls `hello`,
and checks its return and synchronous output length. The backend compares exact
stdout bytes and reads a separate JSON report. **Use the CLI, not a direct Node
harness invocation:** stdout must be an initially empty backend-managed private
regular file to capture console and direct file-descriptor writes correctly.

## Edge Cases

The blank intentionally throws until implemented. Wrong static APIs, syntax,
runtime errors, extra/missing newlines, delayed output, or wrong returns fail.
Broken config/probe/harness or missing tools block; early exit without a trustworthy
report is indeterminate, not a pass. This is not a sandbox.

Keep canonical blanks on `main` and learner edits on a practice branch. `practice`
creates a branch only from clean main, otherwise reuses an existing non-main branch;
dirty main blocks. `start` and `reset` require an existing non-main branch. A new
blank must be reviewed and committed at its path on local main before reset works.
Save before checking/resetting and do not edit during either. Checks are manual;
there is no watch mode, automatic advancement, progress store, or database.

## Example usage

After building/installing the shared CLI and explicitly installing the compiler:

```sh
polyglot list --language typescript
polyglot show typescript/hello
polyglot practice typescript/hello
# Edit and save the displayed file, then press Enter to check.
```

On an existing non-main branch:

```sh
polyglot start typescript/hello
polyglot check typescript/hello
polyglot check typescript
polyglot --node /path/to/node --tsc /path/to/typescript/bin/tsc check typescript/hello
```

After the committed-main prerequisite is met, `polyglot reset typescript/hello`
confirms a single-file reset; preserve its printed backup and recovery artifacts.

## Related files

- [Package](package.json), [lockfile](package-lock.json), [runtime harness](tests/check_hello.cjs)
- [Adapter](../../cli/src/adapters/typescript.rs), [bindings](../../cli/src/model.rs)
- [Checked example](solutions/curated/hello_world.ts): compare after attempting;
  checked against current native tests, not proof of all behavior. Root tests copy
  its text into disposable learner files, never real attempts.
- [Native regressions](../../tests/test_additional_hello.py), [full inventory](../../README/katas/index.md)
