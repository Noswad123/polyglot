from .config import KATAS_DIR
from .db import get_connection
from .editor import open_editor
from .test_runner import run_tests
from .trackables import update_progress


def fetch_previous_solution(kata_name: str, language: str) -> str | None:
    with get_connection() as db:
        cursor = db.execute(
            """
            SELECT e.code_snippet
            FROM examples e
            JOIN trackables AS k ON k.id = e.concept_trackable_id
            JOIN trackables AS l ON l.id = e.language_trackable_id
            WHERE k.name = ? AND l.name = ? AND e.explanation = 'success'
            """,
            (kata_name, language),
        )
        row = cursor.fetchone()
    return row[0] if row else None


def store_successful_solution(kata_name: str, language: str, code: str) -> None:
    with get_connection() as db:
        k_row = db.execute(
            "SELECT id FROM trackables WHERE name = ? AND type = 'kata'",
            (kata_name,),
        ).fetchone()
        l_row = db.execute(
            "SELECT id FROM trackables WHERE name = ? AND type = 'language'",
            (language,),
        ).fetchone()

        if not k_row or not l_row:
            print("⚠️ Could not find trackable entries for kata or language.")
            return

        k_id = k_row[0]
        l_id = l_row[0]

        exists = db.execute(
            """
            SELECT 1 FROM examples
            WHERE language_trackable_id = ?
              AND concept_trackable_id = ?
              AND explanation = 'success'
            """,
            (l_id, k_id),
        ).fetchone()

        if not exists:
            db.execute(
                """
                INSERT INTO examples (language_trackable_id, concept_trackable_id, code_snippet, explanation)
                VALUES (?, ?, ?, 'success')
                """,
                (l_id, k_id, code),
            )
        else:
            print("ℹ️ Already marked as successfully solved. No update stored.")


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


def get_kata_instructions(kata_name: str) -> str:
    path = KATAS_DIR / kata_name / "instructions.md"
    return path.read_text() if path.exists() else ""


def handle_kata(
    kata_name: str,
    language: str,
    file: bool = False,
    answer: bool = False,
    edit: bool = False,
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

    print(f"Opening buffer for kata '{kata_name}' in {language}...\n")

    if file:
        user_code = get_kata_code(kata_name, language)
        if edit:
            user_code = open_editor(user_code)
    else:
        kata_instructions = get_kata_instructions(kata_name)
        user_code = open_editor(kata_instructions)

    print("\nRunning tests...")
    success = run_tests(kata_name, language, user_code)
    if success:
        print("✅ Success! Storing your solution.")
        store_successful_solution(kata_name, language, user_code)
        update_progress(kata_name, "kata", "mastered")
    else:
        print("❌ Tests failed. Try again.")
