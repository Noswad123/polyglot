import subprocess
import tempfile

from .config import KATAS_DIR


def run_python_tests(kata_name: str, user_code: str) -> bool:
    test_file = KATAS_DIR / kata_name / f"test_{kata_name}.py"
    if not test_file.exists():
        print(f"❌ No test file found at: {test_file}")
        return False

    with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as tmp:
        tmp.write(user_code)
        tmp.flush()
        try:
            subprocess.check_call(["pytest", str(test_file), "--tb=short"])
            return True
        except subprocess.CalledProcessError:
            return False


def run_tests(kata_name: str, language: str, user_code: str) -> bool:
    language = language.lower()
    if language == "python":
        return run_python_tests(kata_name, user_code)
    else:
        print(f"⚠️ No test runner implemented for language '{language}'.")
        return False
