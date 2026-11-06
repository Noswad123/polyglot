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
IDS = ("python/hello", "python/find_in_string", "python/length_of_last_word",
       "python/binary_search", "python/fibonacci", "rust/hello")
SOLUTIONS = {
    "hello": 'def hello():\n    print("Hello, World!")\n',
    "find_in_string": "def find_in_string(string, substring):\n    return string.find(substring)\n",
    "length_of_last_word": "def length_of_last_word(text):\n    words = text.split()\n    return len(words[-1]) if words else 0\n",
    "binary_search": """def binary_search(target: int, arr: list[int]) -> bool:
    low, high = 0, len(arr)
    while low < high:
        middle = (low + high) // 2
        if arr[middle] == target:
            return True
        if arr[middle] < target:
            low = middle + 1
        else:
            high = middle
    return False
""",
    "fibonacci": """def fibonacci(length: int) -> list[int]:
    result = []
    first, second = 1, 1
    for _ in range(length):
        result.append(first)
        first, second = second, first + second
    return result
""",
}
RUST_SOLUTION = 'pub fn greeting() -> &\'static str { "Hello, World!" }\n'


def copy_active_fixture(root):
    for language, names in {
        "python": ("exercises", "tests", "README.md"),
        "rust": ("Cargo.toml", "Cargo.lock", "checks.rs", "exercises"),
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
    rust_readme = REPO / "practice/rust/README.md"
    (root / "practice/rust/README.md").write_bytes(
        rust_readme.read_bytes() if rust_readme.is_file() else b"Rust fixture prompt.\n")


def exercise_path(root, language="python", name="hello"):
    return root / "practice" / language / "exercises" / (name + (".py" if language == "python" else ".rs"))


def solve(root, language, name=None):
    if language == "rust":
        exercise_path(root, language).write_text(RUST_SOLUTION)
    else:
        for selected in ((name,) if name else SOLUTIONS):
            exercise_path(root, language, selected).write_text(SOLUTIONS[selected])
