import os
import subprocess
import sys

from ...config import PROJECT_ROOT, PYTHON_KATAS_DIR, TESTS_DIR

ANSWER_DIR = PROJECT_ROOT / "build" / "katas"

def run_python_tests(kata_name: str, user_code: str) -> bool:
    """
    Run pytest for a kata by writing `user_code` into build/katas/<kata_name>.py.
    We then put `build/` on PYTHONPATH before the compatibility package so that
    `from katas.<kata_name> import ...` uses the shadow module.
    """
    test_file = TESTS_DIR / f"test_{kata_name}.py"
    if not test_file.exists():
        print(f"❌ No test file found at: {test_file}")
        return False

    ANSWER_DIR.mkdir(parents=True, exist_ok=True)
    (ANSWER_DIR / "__init__.py").touch()
    solution_file = ANSWER_DIR / f"{kata_name}.py"
    solution_file.write_text(user_code)

    # Keep submitted code ahead of stored solutions, without exposing queue.py.
    env = os.environ.copy()

    if PROJECT_ROOT is None:
        raise ValueError("Not at project root")

    pythonpath_parts = [
        str(ANSWER_DIR.parent),  # build/
        str(PYTHON_KATAS_DIR / "compat"),
    ]
    existing = env.get("PYTHONPATH")
    if existing:
        pythonpath_parts.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pytest", str(test_file), "--tb=short"],
            cwd=PROJECT_ROOT,
            env=env,
        )
        return True
    except subprocess.CalledProcessError:
        return False
    finally:
        try:
            solution_file.unlink()
        except FileNotFoundError:
            pass


def run_tests(kata_name: str, language: str, user_code: str) -> bool:
    language = language.lower()
    if language == "python":
        return run_python_tests(kata_name, user_code)
    else:
        print(f"⚠️ No test runner implemented for language '{language}'.")
        return False
