# Polyglot

A personal programming practice space inspired by Rustlings: small exercises,
immediate feedback, and repeated attempts across the languages I'm studying.

**Darkness holds the explanations. Polyglot holds the executable practice.**

Start simple, practice often, and develop idiomatic fluency. Multiple languages
are welcome; implementing every concept in every language is not a requirement.

## Direction and current status

The accepted direction is a **Rust-based shared workflow with native language
adapters**, preserving the Rustlings-style interaction across languages. See
[ADR 0001](README/decisions/0001-shared-workflow-language-adapters.md).

The commands below use the working Python prototype. A Rust replacement is planned,
not implemented; the prototype and existing practice files remain usable until
the two-language proof and adoption gates in the roadmap pass.

## Start practicing

The [Python starter track](practice/python/README.md) is the first self-contained
practice path. It needs Python 3.11+ and no third-party packages or database.
Python is the initial working example, not a prescribed primary language.

From the repository root:

```sh
python3 polyglot.py list --language python
python3 polyglot.py start python/hello

# Edit practice/python/answers.py, starting with hello(). Then check it:
python3 polyglot.py check python/hello
```

An unimplemented starter should fail. Make that check pass, then follow the
[track instructions](practice/python/README.md) for the next exercise.
`start` preserves existing answers; it does not reset your work. All three exercises
share one answer file. Use `python3 polyglot.py check python` to check the whole
track. The CLI works from another directory when invoked by its absolute script
path, and uses the Python interpreter that launched it.

The CLI is a repository-local script, not yet an installed `polyglot` command.
Direct native commands remain available in the track instructions.

The three exercises are a small setup-and-feedback path, not a full curriculum:

1. **Hello World:** functions and observable output; skip quickly if familiar.
2. **Find in String:** return values and text searches.
3. **Length of Last Word:** text cleanup and edge cases.

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
- **This repository:** exercise prompts, starters, checks, runnable code, and
  instructions needed to run it. Small illustrative snippets may still live in notes.
- **Polyglot CLI:** one front door for listing, starting, and checking practice.
  It delegates to native tools; it does not manage your notes or learning goals.
- **Optional platform work:** the older `pylearn` CLI, database, frontend, and
  backend remain separate experiments. None is required for the starter track.

## Find your way around

- [Roadmap](ROADMAP.md): boundaries, phased work, acceptance criteria, and deferrals.
- [Target architecture](README/architecture.md): Darkness as knowledge, Polyglot as
  practice, and a shared Rust workflow with native adapters as the target.
- [Architecture decision](README/decisions/0001-shared-workflow-language-adapters.md):
  adapter boundaries, outcome semantics, and adoption gates.
- [Python starter track](practice/python/README.md): prompts, checks, and retry instructions.
- [Existing language code](src/): katas, scripts, projects, and experiments with
  varying levels of completeness. Existing implementations may reveal solutions.
- [Older kata catalog and ideas](README/katas/index.md): a resource, not an active queue.
- [Earlier vision](README/vision.md): preserved philosophy and platform proposals.

Only the starter track is documented here as a self-contained practice path.
Keep the active scope small; use a few real sessions to decide what to add next.

## Check the CLI implementation

These integration tests use disposable practice copies, not your local answers:

```sh
python3 -m unittest discover -s tests -p test_polyglot_cli.py -v
```
