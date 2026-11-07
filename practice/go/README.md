# Go practice track

[Home](../../README.md) · [Shared CLI](../../README/rust-cli.md) · [Exercise lifecycle](../../README/exercises.md)

## Overview

One active binding, `go/hello`, uses the shared
[Hello World contract](../../README/katas/hello_world.md). Use **Go 1.20+**;
no third-party dependencies, module setup, server, or database is required.
Legacy `helloWorld.go`, Pong, and Users remain inventory-only and are not built by
this check. Metadata commands are read-only and need no Go toolchain.

## API / Interfaces

Implement `func Hello() string` in `package exercises` in
[exercises/hello.go](exercises/hello.go). Return exactly `Hello, World!` without a
newline; printing is not a substitute. The harness binds `Hello` to `func() string`
to check name, visibility, parameters, and return type.

The adapter selects `--go PATH` or `go` on PATH and probes `go version`, requiring
a recognized `go1.x` version with minor at least 20. Global overrides, including
`--root`, go before the command. It never downloads a toolchain automatically.

## Data Flow

The adapter copies only the selected exercise and [test](tests/hello_test.go) into
private temporary scratch as `hello.go` and `hello_test.go`, then runs
`go test -json -count=1 -run ^TestHello$ hello.go hello_test.go` there.
It sets `GO111MODULE=off`, `GOWORK=off`, `GOPROXY=off`, `GOSUMDB=off`,
`GOTOOLCHAIN=local`, `GOENV=off` and removes `GOFLAGS`. This offline, isolated check
does not build neighboring programs or the Users project. Native Go caches may
still be written. Success requires JSON evidence that `TestHello` ran and passed
and that the package passed normally, not a greeting or pass word on stdout.

## Edge Cases

The blank intentionally panics. Wrong package/signature, syntax errors, panic, or
a returned newline fail. Broken harnesses, zero/renamed tests, and skipped tests
do not pass; early exit without normal test completion is indeterminate.
Go checks the returned value; it is not the printing-binding stdout grader.

Keep learner edits on a practice branch. `practice` branches only from clean main
or reuses an existing non-main branch; dirty main blocks without stashing.
`start`/`reset` require an existing non-main branch. Every new blank must be reviewed
and committed at its path on local main before reset can restore it. Save before
checking/resetting and do not edit during either. Checks are manual, with no watch
mode, automatic advancement, persisted progress, or database.

## Example usage

From the repository root with the shared CLI built/installed:

```sh
polyglot list --language go
polyglot show go/hello
polyglot practice go/hello
# Edit and save the displayed file, then press Enter to check.
```

On an existing non-main branch:

```sh
polyglot start go/hello
polyglot check go/hello
polyglot check go
polyglot --go /path/to/go check go/hello
```

Use the CLI for the isolated offline workflow rather than `go test ./...` in this
mixed legacy collection. After the baseline prerequisite is met,
`polyglot reset go/hello` confirms a single-file reset; preserve both printed
backup and recovery paths.

## Related files

- [Go adapter](../../cli/src/adapters/go.rs), [bindings](../../cli/src/model.rs)
- [Checked example](solutions/curated/hello_world.go): compare after attempting;
  checked against current native tests, not proof of all behavior. Root tests copy
  its text into disposable learner files, never real attempts.
- [Native regressions](../../tests/test_additional_hello.py), [full inventory](../../README/katas/index.md)
