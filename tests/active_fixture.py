"""Copy only active exercise fixtures; never copy learner answers or bytecode."""

from pathlib import Path
import shutil


REPO = Path(__file__).resolve().parents[1]
QUESTIONS = {
    "hello-world": "hello_world.md",
    "find-in-string": "find_in_string.md",
    "length-of-last-word": "lengthOfLastWord.md",
    "binary-search": "binarySearch.md",
    "fibonacci": "fibonacci.md",
}
NAMES = ("hello", "find_in_string", "length_of_last_word", "binary_search", "fibonacci")
IDS = tuple(f"{language}/{name}" for language in ("python", "rust") for name in NAMES)
EXAMPLE_PATHS = {
    language: {name: REPO / "practice" / language / directory / "curated" /
               (("hello_world" if name == "hello" else name) + suffix) for name in NAMES}
    for language, directory, suffix in (("python", "soutions", ".py"),
                                        ("rust", "solutions", ".rs"))
}
# Published examples are inputs, never imported or evaluated in the source tree.
SOLUTIONS = {name: path.read_text() for name, path in EXAMPLE_PATHS["python"].items()}
RUST_SOLUTIONS = {name: path.read_text() for name, path in EXAMPLE_PATHS["rust"].items()}
RUST_SOLUTION = RUST_SOLUTIONS["hello"]


def copy_active_fixture(root):
    for language, names in {
        "python": ("exercises", "tests", "README.md"),
        "rust": ("Cargo.toml", "Cargo.lock", "checks.rs", "exercises", "tests", "README.md"),
    }.items():
        destination = root / "practice" / language
        destination.mkdir(parents=True)
        for name in names:
            source = REPO / "practice" / language / name
            if source.is_dir():
                shutil.copytree(source, destination / name,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            else:
                shutil.copy2(source, destination / name)
    shutil.copy2(REPO / ".gitignore", root / ".gitignore")
    for source in (REPO / "README/katas").glob("*.md"):
        if source.name == "index.md":
            continue
        destination = root / source.relative_to(REPO)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def exercise_path(root, language="python", name="hello"):
    return root / "practice" / language / "exercises" / (name + (".py" if language == "python" else ".rs"))


def solve(root, language, name=None):
    solutions = RUST_SOLUTIONS if language == "rust" else SOLUTIONS
    for selected in ((name,) if name else solutions):
        exercise_path(root, language, selected).write_text(solutions[selected])
