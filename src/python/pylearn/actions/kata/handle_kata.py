from ...config import KATAS_DIR
from .common import build_initial_buffer, fetch_previous_solution, run_kata_once


def get_kata_code(kata_name: str, language: str) -> str:
    extension_map = {"python": "py", "javascript": "js", "java": "java"}
    ext = extension_map.get(language.lower())
    if not ext:
        print(f"⚠️ No extension mapping for language: {language}")
        return ""

    file_path = KATAS_DIR / kata_name / f"{kata_name}.{ext}"
    if not file_path.exists():
        print(f"❌ No solution file found at: {file_path}")
        return ""

    return file_path.read_text()


def handle_kata(
    kata_name: str,
    language: str,
    file: bool = False,
    answer: bool = False,
):
    if answer:
        prev = fetch_previous_solution(kata_name, language)
        if prev:
            print("\nPrevious solution:\n" + "-" * 40)
            print(prev)
            print("-" * 40)
            return
        else:
            print("ℹ️ No previous successful solution found.\n")

    language = language.lower()
    if language != "python":
        print("Only supporting python at this time")
        return

    print(f"Opening buffer for kata '{kata_name}' in {language}...\n")

    # If you have a canonical solution file you want to preload, grab it here.
    existing_code: str | None = None
    if file:
        existing_code = get_kata_code(kata_name, language)

    buffer_content = build_initial_buffer(
        kata_name=kata_name,
        language=language,
        existing_code=existing_code,
    )

    success, _ = run_kata_once(
        kata_name=kata_name,
        language=language,
        initial_buffer=buffer_content,
    )

    if not success:
        print("❌ Tests failed. Try again.")
