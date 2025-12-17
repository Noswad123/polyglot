from __future__ import annotations

from ...config import KATAS_DIR
from ...db import get_connection
from ...editor import open_editor
from .test_runner import run_tests
from ..trackables import update_progress


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


def get_kata_instructions(kata_name: str) -> str:
    """
    Reads the instructions for a kata.

    Adjust this path logic to match your actual layout:
    e.g. README/katas/boggle.md or KATAS_DIR / f"{kata_name}.md"
    """
    # Example: README/katas/boggle.md (from your debug output)
    path = KATAS_DIR / f"{kata_name}.md"

    return path.read_text() if path.exists() else ""


# ──────────────────────── Shared core logic ────────────────────────


def build_initial_buffer(
    kata_name: str,
    language: str,
    existing_code: str | None = None,
) -> str:
    """
    Build an initial buffer for the editor:

    - Title line
    - Commented instructions (for Python, so they don't break tests)
    - Either existing code or a stub line.
    """
    language = language.lower()
    header_line = f"# {kata_name} – solution in {language}\n\n"

    instructions = get_kata_instructions(kata_name)

    if language == "python":
        if instructions:
            commented = []
            for line in instructions.splitlines():
                if line.strip():
                    commented.append("# " + line)
                else:
                    commented.append("#")
            instructions_block = "\n".join(commented) + "\n\n"
        else:
            instructions_block = "# (No instructions found for this kata.)\n\n"

        if existing_code and existing_code.strip():
            body = existing_code.rstrip() + "\n\n"
        else:
            body = "# Write your solution below this line.\n\n"

        return header_line + instructions_block + body

    # Fallback for future non-Python languages
    if instructions:
        body = instructions + "\n\n"
    else:
        body = ""
    if existing_code and existing_code.strip():
        body += existing_code.rstrip() + "\n\n"
    else:
        body += f"// {kata_name} solution in {language}\n\n"

    return header_line + body


def run_kata_once(
    kata_name: str,
    language: str,
    initial_buffer: str,
) -> tuple[bool, str]:
    """
    Open the editor with `initial_buffer`, then run tests on the result.

    Returns (success, final_code).
    """
    # Let the user edit the buffer
    user_code = open_editor(initial_buffer, suffix=".py")

    print("\nRunning tests...")
    success = run_tests(kata_name, language, user_code)

    if success:
        print("✅ Success! Storing your solution.")
        store_successful_solution(kata_name, language, user_code)
        update_progress(kata_name, "kata", "mastered")

    return success, user_code
def get_kata_instructions(kata_name: str) -> str:
    path = KATAS_DIR / f"{kata_name}.md"
    if not path.exists():
        return ""
    text = path.read_text()
    return text

