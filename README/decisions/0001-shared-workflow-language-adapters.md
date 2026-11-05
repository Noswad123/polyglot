# ADR 0001: Shared practice workflow with native language adapters

**Status:** Accepted direction; Rust implementation not started.

[Architecture](../architecture.md) · [Roadmap](../../ROADMAP.md)

## Context

Polyglot is intended to offer the Rustlings user flow across several programming
languages. The desired experience is select → edit → check → hint → next, with
watching and resume support introduced incrementally. Rust is the chosen host
language for that experience, not the required exercise language.

The current `polyglot.py` is a useful Python-only prototype. Its three exercises
share `practice/python/answers.py` but select different unittest methods. It
establishes preservation and invocation behavior, not the final architecture.

Rustlings demonstrates the interaction we want, but its current execution path
includes Cargo build/test/Clippy, Rust binary execution, and `.rs` paths. Reusing
its interaction does not mean preserving those assumptions in the shared workflow.

## Decision

Build one Rust-based CLI with a language-independent workflow and built-in native
language adapters. Prove the boundary with Python and Rust before expanding it.
Use native language checks rather than creating a universal compiler/test engine.

Borrow Rustlings interaction patterns and selectively adapt suitable code. Do not
adopt a full fork as the default implementation strategy. Before copying code,
record the upstream revision and retain required MIT license/copyright notices.

This supersedes the earlier prototype-only scope that deferred an internal adapter
boundary. Dynamic plugins and a generalized runner framework remain out of scope.

## Responsibility boundaries

### Shared workflow

Own exercise selection, safe attempt preparation, check orchestration, result
presentation, and eventually hints, navigation, watching, and resume policy.

It must not construct Cargo commands, understand Python imports, or scatter
language conditionals throughout application state. Select an adapter at one
dispatch boundary and use the same orchestration for both languages.

### Exercise definition

Carry a stable language-qualified ID, language, title, prompt/hint references,
workspace identity, starter-to-attempt mapping, native check selector, and optional
Darkness references. Define only the fields required by the first two adapters;
the serialization format is an implementation choice, not a reason to build a DSL.

Exercise identity is distinct from workspace identity. The current three Python
exercises must be able to share an answer file while selecting different checks.
A Cargo target need not have the same layout as a Python module.

### Language adapter

Resolve and validate its toolchain, translate the native check selector into an
invocation, and classify results using evidence from that toolchain.

Initially, two concrete adapters and a small internal interface or enum are enough.
Do not introduce plugin discovery, dynamic loading, an adapter SDK, or arbitrary
shell commands in exercise metadata.

Adapters do not select the next exercise, update personal notes, record mastery,
or overwrite attempts. Add language-specific preparation hooks only when a real
exercise requires them; ordinary starter preservation is shared behavior.

### Process execution and workspace preparation

Execute argument vectors without shell interpolation. Supply an explicit working
directory, preserve native diagnostic output, and retain process exit/signal
information. Validate exercise paths against the intended workspace boundaries.

Prepare attempts with exclusive creation, preserving existing files. `check` never
creates or resets answers. Reject path conflicts clearly. Define partial-preparation
behavior before supporting multi-file attempts; do not silently repair existing
workspaces from newer starters.

Native tools may write normal build artifacts. Preservation means protecting
learner sources, not promising that checking writes nothing. Running exercise code
uses the user's privileges; this is not a sandbox for untrusted exercise packs.

## Check outcomes

- **Passed:** the intended check actually ran and succeeded. Selecting zero tests
  is not a passing exercise.
- **Attempt failed:** learner code did not satisfy the check, including intentional
  starters, assertion failures, syntax/compile errors, and runtime failures.
- **Blocked:** missing tools, invalid check configuration, broken harness, or
  dependency/toolchain setup prevents meaningful checking.
- **Interrupted/indeterminate:** cancellation, termination, or insufficient evidence
  prevents a trustworthy classification.

Do not treat every nonzero exit as learner failure. Where an adapter cannot
reliably distinguish causes, report uncertainty and native diagnostics rather
than inventing a result. The first slice must detect known missing-tool and
invalid-target cases; exhaustive diagnostic parsing is not required.

## Python tool selection

A Rust host cannot rely on Python's `sys.executable`. Define and document explicit
resolution: user override → documented repository virtual environment → PATH
fallback. Validate the supported version and make the resolved interpreter visible.
Do not automatically install dependencies, create environments, or silently switch
interpreters after a check fails.

## Delivery and adoption gates

1. **Two-language vertical slice:** list/start/check uses the same Rust workflow
   for the existing Python exercises and one isolated Rust exercise. No watcher,
   persisted progress, TUI, or automatic reset is required for this proof.
2. **Interaction parity:** add hints and navigation, then watching, while keeping
   native commands and explicit check mode usable.
3. **Resume:** persist minimal local session state only after check semantics and
   workspace invalidation are established.
4. **Adoption:** demonstrate real sessions and preservation/behavior parity before
   proposing retirement or wrapping of `polyglot.py`. Do not remove existing code
   or migrate user attempts as a side effect of introducing Rust.

The [roadmap](../../ROADMAP.md) defines acceptance checks for each gate.

## Watching and progress constraints

One source file is not necessarily one exercise. Watch declared workspace/check
inputs, accounting for the shared Python answer file and relevant tests/config.
Prevent overlapping or superseded runs from publishing stale success results.

Persisted progress must not treat an old pass as current validity after edits.
Completion history, current check validity, and mastery are different concepts.
Adapters report outcomes; shared session policy controls navigation and persistence.

## Knowledge boundary

Darkness remains authoritative for general explanations, personal learning goals,
and reflections. Polyglot owns executable practice and any future local attempt
history. References are optional links, not a shared database or synchronization
requirement. No adapter or workflow step automatically edits Darkness.

## Alternatives and consequences

- **Extend Python indefinitely:** technically feasible and fastest initially, but
  not the chosen Rust-hosted direction. Keep it as the compatibility baseline.
- **Generalize a full Rustlings fork:** potentially saves interaction work, but
  brings Cargo-centric assumptions and upstream maintenance. Selective reuse keeps
  the scope smaller; a substantial fork would require revisiting this decision.
- **Separate application per language:** duplicates the user flow and makes
  consistent behavior harder to maintain. Rejected in favor of shared orchestration.

Rust adds compilation and distribution work. It does not inherently make adapters
more extensible than Python; the boundary does. The two-language proof is intended
to catch a Rust-only design before more features or exercise tracks depend on it.

## Upstream references

- [Rustlings exercise execution](https://github.com/rust-lang/rustlings/blob/main/src/exercise.rs)
- [Rustlings application state](https://github.com/rust-lang/rustlings/blob/main/src/app_state.rs)
- [Rustlings license](https://github.com/rust-lang/rustlings/blob/main/LICENSE)

These links describe the reviewed design, not a pinned code dependency. Pin a
revision if implementation copies code; no upstream code is copied by this ADR.
