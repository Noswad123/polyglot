# Polyglot

A personal programming practice space inspired by Rustlings: small exercises,
immediate feedback, and repeated attempts across the languages I'm studying.

**Darkness holds the explanations. Polyglot holds the executable practice.**

Start simple, practice often, and develop idiomatic fluency. Multiple languages
are welcome; implementing every concept in every language is not a requirement.

## Start practicing

The [Python starter track](practice/python/README.md) is the first self-contained
practice path. It needs Python 3.11+ and no third-party packages, CLI, or database.
Python is the initial working example, not a prescribed primary language.

From the repository root:

```sh
# Once: create local answers without overwriting an existing attempt.
cp -n practice/python/starter.py practice/python/answers.py

# Edit practice/python/answers.py, starting with hello(). Then check it:
python3 -m unittest discover -s practice/python -p test_exercises.py -k hello -v
```

An unimplemented starter should fail. Make that check pass, then follow the
[track instructions](practice/python/README.md) for the next exercise.

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
- **Optional tooling:** the existing CLI, database, frontend, and backend are
  separate platform work. None is required for the starter track.

## Find your way around

- [Roadmap](ROADMAP.md): boundaries, phased work, acceptance criteria, and deferrals.
- [Python starter track](practice/python/README.md): prompts, checks, and retry instructions.
- [Existing language code](src/): katas, scripts, projects, and experiments with
  varying levels of completeness. Existing implementations may reveal solutions.
- [Older kata catalog and ideas](README/katas/index.md): a resource, not an active queue.
- [Earlier vision](README/vision.md): preserved philosophy and platform proposals.

Only the starter track is documented here as a self-contained practice path.
Keep the active scope small; use a few real sessions to decide what to add next.
