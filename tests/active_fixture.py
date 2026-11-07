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
LANGUAGES = ("python", "rust", "typescript", "go", "bash", "lua")
EXTENSIONS = dict(zip(LANGUAGES, (".py", ".rs", ".ts", ".go", ".sh", ".lua")))
PAIRED_IDS = tuple(f"{language}/{name}" for language in LANGUAGES[:2] for name in NAMES)
IDS = PAIRED_IDS + tuple(f"{language}/hello" for language in LANGUAGES[2:])
HELLO_EXAMPLE_PATHS = {
    language: REPO / "practice" / language / "solutions/curated" / ("hello_world" + EXTENSIONS[language])
    for language in LANGUAGES[2:]
}
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


def tool_overrides(missing=None):
    """Keep interpreter shims intact; only tsc must be the actual compiler entry."""
    tools = {name: shutil.which(name) for name in ("node", "go", "bash", "lua")}
    compiler = REPO / "practice/typescript/node_modules/typescript/bin/tsc"
    tools["tsc"] = str(compiler) if compiler.is_file() else None
    return [value for name, path in tools.items() if missing is not None or path
            for value in ("--" + name, str(missing if missing is not None else Path(path).absolute()))]


def copy_active_fixture(root):
    for language, names in {
        "python": ("exercises", "tests", "README.md"),
        "rust": ("Cargo.toml", "Cargo.lock", "checks.rs", "exercises", "tests", "README.md"),
        "typescript": ("exercises", "tests", "package.json", "package-lock.json", "README.md"),
        "go": ("exercises", "tests", "README.md"),
        "bash": ("exercises", "tests", "README.md"),
        "lua": ("exercises", "tests", "README.md"),
    }.items():
        destination = root / "practice" / language
        destination.mkdir(parents=True)
        for name in names:
            source = REPO / "practice" / language / name
            if name == "README.md" and not source.exists():
                continue
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
    return root / "practice" / language / "exercises" / (name + EXTENSIONS[language])


def solve(root, language, name=None):
    solutions = (RUST_SOLUTIONS if language == "rust" else SOLUTIONS if language == "python"
                 else {"hello": HELLO_EXAMPLE_PATHS[language].read_text()})
    for selected in ((name,) if name else solutions):
        exercise_path(root, language, selected).write_text(solutions[selected])
