from ..config import KATAS_DIR
from ..db import get_connection
from ..editor import open_editor
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


def get_kata_instructions(kata_name: str) -> str:
    path = KATAS_DIR / kata_name / "instructions.md"
    return path.read_text() if path.exists() else ""


def _choose_kata() -> str | None:
    katas = sorted(
        [
            p.stem
            for p in KATAS_DIR.glob("*.md")
            if p.name not in {"index.md"}
        ],
        key=str.lower,
    )

    if not katas:
        print("❌ No katas found in KATAS_DIR.")
        return None

    print("🧵 Available katas:")
    for idx, name in enumerate(katas, start=1):
        print(f"  {idx}. {name}")
    print("  q. quit")

    while True:
        choice = input("\nChoose a kata (number or name, 'q' to quit): ").strip()
        if choice.lower() in {"q", "quit"}:
            return None

        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(katas):
                return katas[idx - 1]
            print("⚠️ Invalid index. Try again.")
            continue

        if choice in katas:
            return choice

        print("⚠️ Not a valid kata. Try again.")


def _choose_language() -> str | None:
    languages = ["python"]  # extend later if you want

    print("\n🗣  Available languages:")
    for idx, lang in enumerate(languages, start=1):
        print(f"  {idx}. {lang}")
    print("  q. quit")

    while True:
        choice = input("\nChoose a language (number or name, 'q' to quit): ").strip()
        if choice.lower() in {"q", "quit"}:
            return None

        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(languages):
                return languages[idx - 1]
            print("⚠️ Invalid index. Try again.")
            continue

        lowered = choice.lower()
        for lang in languages:
            if lang.lower() == lowered:
                return lang

        print("⚠️ Not a valid language. Try again.")


def enter_dojo() -> None:
    """
    Interactive kata loop:

    - pick a kata from list
    - select language (currently Python only)
    - open an editor buffer seeded with instructions
    - closing the editor = "I'm done developing"
    - run tests against that buffer
    - on failure: re-edit, see previous solution, or quit
    - on success: store solution and update progress
    """

    print("🥋 Welcome to the dojo!\n")

    kata_name = _choose_kata()
    if kata_name is None:
        print("👋 Leaving the dojo.")
        return

    language = _choose_language()
    if language is None:
        print("👋 Leaving the dojo.")
        return

    print(f"\n🥊 Entering kata '{kata_name}' in {language}...\n")

    # Seed buffer with instructions (commented for Python so they don't break tests)
    instructions = get_kata_instructions(kata_name)
    if instructions and language.lower() == "python":
        commented = []
        for line in instructions.splitlines():
            if line.strip():
                commented.append("# " + line)
            else:
                commented.append("#")
        header = "\n".join(commented)
        user_code = header + "\n\n# Write your solution below\n\n"
    elif instructions:
        user_code = instructions + "\n\n"
    else:
        user_code = f"# {kata_name} – solution in {language}\n\n"

    while True:
        # This is the “I’m done” signal: once you close the editor, we get the buffer.
        user_code = open_editor(user_code, suffix=".py")

        print("\nRunning tests...")
        success = run_tests(kata_name, language, user_code)

        if success:
            print("✅ Success! Storing your solution.")
            store_successful_solution(kata_name, language, user_code)
            update_progress(kata_name, "kata", "mastered")

            while True:
                action = input(
                    "\nOptions: [s]ee previous solution, [q]uit dojo: "
                ).strip().lower()
                if not action or action.startswith("q"):
                    print("🎉 Well done. Leaving the dojo.")
                    return
                if action.startswith("s"):
                    prev = fetch_previous_solution(kata_name, language)
                    if prev:
                        print("\nPrevious solution:\n" + "-" * 40)
                        print(prev)
                        print("-" * 40)
                    else:
                        print("ℹ️ No previous successful solution stored yet.")
                else:
                    print("⚠️ Unknown option. Try again.")
        else:
            print("❌ Tests failed.")
            while True:
                action = input(
                    "\nOptions: [e]dit again, [s]ee previous solution, [q]uit dojo: "
                ).strip().lower()
                if not action or action.startswith("e"):
                    # break inner loop and reopen the editor with current buffer
                    break
                if action.startswith("s"):
                    prev = fetch_previous_solution(kata_name, language)
                    if prev:
                        print("\nPrevious solution:\n" + "-" * 40)
                        print(prev)
                        print("-" * 40)
                    else:
                        print("ℹ️ No previous successful solution found.\n")
                elif action.startswith("q"):
                    print("👋 Leaving the dojo. Come back soon.")
                    return
                else:
                    print("⚠️ Unknown option. Try again.")
