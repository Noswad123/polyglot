"""Small, local entry point for the Python practice track (Python 3.11+)."""

import argparse
from pathlib import Path
import shlex
import subprocess
import sys


EXERCISES = {
    "hello": "Hello World",
    "find_in_string": "Find in String",
    "length_of_last_word": "Length of Last Word",
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="List available practice exercises")
    listing.add_argument("--language", choices=("python",))
    start = commands.add_parser("start", help="Create or preserve a shared answer file")
    start.add_argument("target", help="python/EXERCISE")
    check = commands.add_parser("check", help="Run native unittest checks")
    check.add_argument("target", help="python or python/EXERCISE")
    args = parser.parse_args(argv)

    if args.command == "list":
        for exercise, title in EXERCISES.items():
            print(f"python/{exercise} - {title} ({exercise}())")
        return 0

    valid_targets = [f"python/{name}" for name in EXERCISES]
    if args.command == "check":
        valid_targets.append("python")
    if args.target not in valid_targets:
        parser.error(f"unknown target {args.target!r}; choose: {', '.join(valid_targets)}")

    root = Path(__file__).resolve().parent
    track = root / "practice" / "python"
    answers = track / "answers.py"
    invocation = [sys.executable, str(root / "polyglot.py")]
    exercise = args.target.partition("/")[2]
    try:
        if answers.is_symlink() or (answers.exists() and not answers.is_file()):
            parser.error(
                f"{answers} must be a regular file, not a symlink or directory; "
                "move it aside before retrying"
            )
        if args.command == "start":
            starter = (track / "starter.py").read_bytes()
            try:
                with answers.open("xb") as output:
                    output.write(starter)
                status = "Created"
            except FileExistsError:
                # Exclusive creation preserves attempts, including a concurrent start.
                if answers.is_symlink() or not answers.is_file():
                    parser.error(f"{answers} must be a regular file; move it aside before retrying")
                status = "Preserved"
            print(f"{status}: {answers}")
            print(f"Exercise: {EXERCISES[exercise]} ({exercise}())")
            print(f"Prompt: {track / 'README.md'}")
            print(f"Next: {shlex.join([*invocation, 'check', args.target])}")
            return 0

        if not answers.is_file():
            start_command = shlex.join([*invocation, "start", f"python/{exercise or 'hello'}"])
            parser.error(
                f"missing {answers}; run: "
                f"{start_command}"
            )
        target = (
            f"test_exercises.PracticeTests.test_{exercise}"
            if exercise else "test_exercises"
        )
        return subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "-f", "-v", target],
            cwd=track,
            check=False,
        ).returncode
    except OSError as error:
        parser.error(f"cannot {args.command} {args.target}: {error}")


if __name__ == "__main__":
    sys.exit(main())
