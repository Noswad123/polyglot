# Target architecture

[Home](../README.md) · [Roadmap](../ROADMAP.md)

**Accepted direction:** a Rust-hosted, Rustlings-inspired shared workflow with
native language adapters. The current Python CLI remains a working prototype;
the Rust replacement has not been implemented. See
[ADR 0001](decisions/0001-shared-workflow-language-adapters.md) for the decision,
boundaries, and adoption gates.

## One system, three responsibilities

**Darkness = knowledge. Polyglot = practice. The CLI = access. A web UI is optional.**

Polyglot is one practice system with an interface, not a backend product and a CLI
product that must be completed independently.

```text
You
 |
Shared Rust workflow (target)
select → edit → check → hint → next
 |
Exercise definition + safe workspace preparation
 |
Language adapter -------- native language tools
 |                           Python / Cargo / ...
Polyglot practice files
 |
references to concepts
 |
Darkness
```

The references are links, not a requirement to import notes into a shared database.

## Darkness: authoritative knowledge

Darkness owns explanations, mental models, language comparisons, resources,
personal learning goals, and learning takeaways. It answers:

> What does this mean, and what have I learned?

Small illustrative snippets belong here when useful. Full runnable exercise
solutions and test infrastructure belong in Polyglot.

## Polyglot: executable practice

Polyglot owns prompts, starters, checks, runnable examples, and local attempts. It
answers:

> What can I practice, and did this attempt work?

The initial storage is files in this repository. A future attempt/review history
would belong to Polyglot, not to a concept note's completeness status. Passing one
exercise is evidence about an attempt, not a declaration of mastery.

No backend service or database is needed for the current practice path. A future
storage choice should follow a concrete requirement, not precede it.

## Shared workflow and native adapters (target)

The Rust workflow owns selection, safe preparation, check orchestration, feedback,
hints, and navigation. Watching and resume follow in separate delivery gates.
It must not contain Cargo/Python command construction or assume `.rs` files.

Exercise definitions connect stable IDs to workspaces, prompts, hints, native check
selectors, and optional notes. Multiple exercises can share one workspace; native
layouts need not be identical across languages.

Python and Rust adapters resolve their tools, invoke the selected native checks,
and return evidence-backed outcomes: passed, attempt failed, blocked, or
interrupted/indeterminate. Keep native diagnostics; do not mistake missing tools
for an incorrect solution or zero selected tests for success.

Use two built-in adapters, not a dynamic plugin framework. Prove both languages
through the same list/start/check path before adding interactive conveniences.
Reuse suitable Rustlings patterns/code without importing Cargo assumptions into
application state or adopting a full fork by default.

## Current interface: Python prototype

The working interface remains repository-local:

```sh
python3 polyglot.py list --language python
python3 polyglot.py start python/hello
python3 polyglot.py check python/hello
python3 polyglot.py check python
```

It currently supports only the existing three Python starter exercises. They share
one local `answers.py` file. Selecting another exercise does not reset that file.
`check` does not create or reset answers, and failure is reported as a nonzero exit
status from the native test runner.

Keep this prototype and direct native commands usable during the Rust proof.
Retirement is gated on real sessions and behavior/preservation parity, not merely
on a Rust binary compiling. No installed Rust `polyglot` command exists yet.
Separate per-language CLIs are not the target; existing `pylearn` code remains
untouched.

## Integration rules

- General explanations remain in Darkness; exercise contracts remain in Polyglot.
- Note references are optional. A missing note or unavailable MindWeaver index
  must not prevent starting or checking an exercise.
- The CLI does not automatically edit notes or synchronize statuses.
- Existing local attempts must never be silently overwritten.
- Direct native check commands remain documented even when a CLI shortcut exists.
- Practice must not depend on a web service, notes database, or progress service.
- A future Rust host must explicitly resolve its Python interpreter rather than
  assuming the host process already supplies one.
- Watch and resume behavior must account for shared workspaces and stale checks;
  completion history must not become a mastery score.

## Later capabilities, not current promises

Once real practice demonstrates the need, the same CLI could provide note lookup,
attempt history, or an exercise-review queue. Reading through MindWeaver is one
possible note-lookup implementation, not a dependency we are adding now.

A UI could use the same exercise contracts later. There is no commitment to build
it, and it should not establish a second source of truth for exercises or notes.

The desired outcome is a short path into useful practice, not a comprehensive
learning-management platform. See the roadmap for the next decision gate.
