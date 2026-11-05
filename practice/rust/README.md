# Rust adapter proof exercise

[Home](../../README.md) · [Rust CLI proof](../../README/rust-cli.md)

One small exercise proves that the shared workflow can use a native Rust check as
well as Python. It is not a complete Rust learning track or a requirement to study
Rust alongside another language.

## Task: `rust/hello`

Implement this function in your local **`practice/rust/answers.rs`**:

```rust
pub fn greeting() -> &'static str
```

Return exactly `Hello, World!`. The check tests the returned value; printing the
message is not sufficient. The starter deliberately uses `todo!()`.

## Through the shared CLI

Build the proof CLI from the repository root:

```sh
cargo build --locked
./target/debug/polyglot start rust/hello
# Edit practice/rust/answers.rs, then:
./target/debug/polyglot check rust/hello
```

`start` preserves an existing answer. `check rust` checks the Rust track, currently
the same single exercise. Missing tools or broken check configuration are blocked
checks, not failed solutions. See the CLI instructions for tool overrides.

## Direct native alternative

From the repository root:

```sh
cp -n practice/rust/starter.rs practice/rust/answers.rs
cargo test --offline --locked --manifest-path practice/rust/Cargo.toml --test practice_checks -- hello --exact
```

The exercise package is independent of the CLI and older Rust projects. It has no
external dependencies. Its checked-in lockfile makes locked offline checks
possible. Cargo writes normal build artifacts under `practice/rust/target/`;
checks should not modify the starter, answers, harness, manifest, or lockfile.

## Retry safely

Save a copy of your answer if you want to keep it, then replace only the function
body with the starter body. There is no automatic reset. `answers.rs` is ignored
by Git and is not backed up by commits; the starter and checks remain reusable.

Hint: a string literal has a static lifetime. Consult the existing Rust notes in
Darkness if useful; no note or notes database is required to run this exercise.
