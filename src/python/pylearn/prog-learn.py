import argparse
import os
import subprocess
import tempfile
from sqlite3 import connect

DB_PATH = "db/programming_languages.db"
KATAS_DIR = "katas"

# -----------------------
# Test runners
# -----------------------

def run_python_tests(kata_name: str, user_code: str) -> bool:
    """
    Writes user_code to a temp file and runs pytest against kata's test file.
    NOTE: This assumes the kata tests import the kata code by name or path.
    """
    test_file = os.path.join(KATAS_DIR, kata_name, "test_" + kata_name + ".py")
    if not os.path.exists(test_file):
        print(f"❌ No test file found at: {test_file}")
        return False

    with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as tmp:
        tmp.write(user_code)
        tmp.flush()
        # You may need to set an env var or patch sys.path so tests can find this file.
        try:
            subprocess.check_call(["pytest", test_file, "--tb=short"])
            return True
        except subprocess.CalledProcessError:
            return False

def run_tests(kata_name: str, language: str, user_code: str) -> bool:
    """
    Dispatch to language-specific test runners.
    For now, only Python is implemented.
    """
    language = language.lower()
    if language == "python":
        return run_python_tests(kata_name, user_code)
    else:
        print(f"⚠️ No test runner implemented for language '{language}'.")
        return False

# -----------------------
# Editor helpers
# -----------------------

def open_editor(initial_code: str = "") -> str:
    """
    Opens $EDITOR (defaults to vim) with initial_code, returns edited text.
    """
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as tmp:
        tmp.write(initial_code)
        tmp.flush()
        subprocess.call([os.environ.get("EDITOR", "vim"), tmp.name])
        tmp.seek(0)
        result = tmp.read()
    os.unlink(tmp.name)
    return result

# -----------------------
# Kata helpers (using trackables + examples)
# -----------------------

def fetch_previous_solution(db, kata_name, language):
    """
    Fetch a previously stored successful solution for (kata, language)
    stored in examples.*_trackable_id with explanation = 'success'.
    """
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

def store_successful_solution(db, kata_name, language, code):
    """
    Store a successful kata solution if one doesn't already exist.
    """
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
        db.commit()
        print("💾 Stored successful solution.")
    else:
        print("ℹ️ Already marked as successfully solved. No update stored.")

def get_kata_code(kata_name: str, language: str) -> str:
    """
    Load existing kata solution from the filesystem (not DB).
    """
    extension_map = {"python": "py", "javascript": "js", "java": "java"}
    ext = extension_map.get(language.lower())
    if not ext:
        print(f"⚠️ No extension mapping for language: {language}")
        return ""

    file_path = os.path.join(KATAS_DIR, kata_name, f"{kata_name}.{ext}")
    if not os.path.exists(file_path):
        print(f"❌ No solution file found at: {file_path}")
        return ""
    with open(file_path, "r") as file:
        return file.read()

def get_kata_instructions(kata_name: str) -> str:
    """
    Load instructions from instructions.md next to the kata.
    """
    path = os.path.join(KATAS_DIR, kata_name, "instructions.md")
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    return ""

def handle_kata(kata_name: str, language: str, file: bool = False,
                answer: bool = False, edit: bool = False):
    db = connect(DB_PATH)

    if answer:
        prev = fetch_previous_solution(db, kata_name, language)
        if prev:
            print("\nPrevious solution:\n" + "-" * 40)
            print(prev)
            print("-" * 40)
            db.close()
            return
        else:
            print("ℹ️ No previous successful solution found.\n")

    print(f"Opening buffer for kata '{kata_name}' in {language}...\n")

    # Either load from a file or pre-load with instructions for scratch coding.
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
        store_successful_solution(db, kata_name, language, user_code)
        # Optionally mark the kata trackable as 'mastered'
        update_progress(db, kata_name, "kata", "mastered")
    else:
        print("❌ Tests failed. Try again.")

    db.close()

# -----------------------
# Concept learning helpers
# -----------------------

def show_concept(db, concept_name: str, language: str | None = None):
    """
    Show examples from the examples(language_id, concept_id) side
    for a given concept, optionally filtered by language.
    """
    params = []
    query = """
        SELECT l.name AS language_name,
               c.name AS concept_name,
               e.code_snippet,
               e.explanation
        FROM examples e
        JOIN languages l ON l.id = e.language_id
        JOIN concepts c ON c.id = e.concept_id
        WHERE c.name = ?
    """
    params.append(concept_name)

    if language:
        query += " AND l.name = ?"
        params.append(language)

    query += " ORDER BY l.name"

    rows = db.execute(query, tuple(params)).fetchall()
    if not rows:
        print("No examples found for that concept (and language, if specified).")
        return

    for i, (lang, concept, code, explanation) in enumerate(rows, start=1):
        print(f"\n=== [{i}] {concept} in {lang} ===")
        print("-------- CODE --------")
        print(code)
        print("----- EXPLANATION ----")
        print(explanation or "(no explanation yet)")
        print("----------------------")

# -----------------------
# Trackables & progress
# -----------------------

def list_items(db, item_type: str):
    cursor = db.execute(
        "SELECT id, name FROM trackables WHERE type = ? ORDER BY name",
        (item_type,),
    )
    rows = cursor.fetchall()
    if not rows:
        print(f"No trackables of type '{item_type}' found.")
        return
    for row in rows:
        print(f"{row[0]}: {row[1]}")

def update_progress(db, name: str, item_type: str, status: str, notes: str | None = None):
    """
    Update trackable_progress for a given trackable by name + type.
    """
    if status not in ("not started", "in progress", "mastered", "abandoned"):
        print(f"❌ Invalid status: {status}")
        return

    row = db.execute(
        "SELECT id FROM trackables WHERE name = ? AND type = ?",
        (name, item_type),
    ).fetchone()

    if not row:
        print(f"❌ No trackable found with name '{name}' and type '{item_type}'.")
        return

    trackable_id = row[0]
    db.execute(
        """
        INSERT INTO trackable_progress (trackable_id, status, notes)
        VALUES (?, ?, ?)
        ON CONFLICT(trackable_id)
        DO UPDATE SET status = excluded.status,
                      notes  = COALESCE(excluded.notes, trackable_progress.notes)
        """,
        (trackable_id, status, notes),
    )
    db.commit()
    print(f"✅ Updated {item_type} '{name}' to status '{status}'.")

def show_status(db, item_type: str | None = None):
    """
    Show status of all trackables or only those of a given type.
    """
    query = """
        SELECT t.type, t.name, COALESCE(p.status, 'not started') AS status
        FROM trackables t
        LEFT JOIN trackable_progress p ON p.trackable_id = t.id
    """
    params = []
    if item_type:
        query += " WHERE t.type = ?"
        params.append(item_type)
    query += " ORDER BY t.type, t.name"

    rows = db.execute(query, tuple(params)).fetchall()
    if not rows:
        print("No trackables found.")
        return

    for ttype, name, status in rows:
        print(f"[{ttype}] {name}: {status}")

# -----------------------
# Main CLI
# -----------------------

def main():
    valid_choices = ["list", "show", "run", "status", "progress", "kata"]
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=valid_choices, help="Command to execute")

    parser.add_argument("--type")      # for list/status/progress
    parser.add_argument("--name")      # concept/kata/project name
    parser.add_argument("--language")  # optional language filter
    parser.add_argument("--update")    # progress update target name (or use --name)
    parser.add_argument("--status")    # new status for progress
    parser.add_argument("--file", action="store_true")
    parser.add_argument("--answer", action="store_true")
    parser.add_argument("--edit", action="store_true")

    args = parser.parse_args()

    db = connect(DB_PATH)

    match args.command:
        case "list":
            if not args.type:
                print("❌ --type is required for 'list' (language|concept|kata|project).")
            else:
                list_items(db, args.type)

        case "show":
            # For now: show concept examples
            if not args.name:
                print("❌ --name (concept name) is required for 'show'.")
            else:
                show_concept(db, args.name, args.language)

        case "run":
            # Could be used later (e.g. run a script/project)
            print("not implemented")

        case "status":
            show_status(db, args.type)

        case "progress":
            target_name = args.update or args.name
            if not (target_name and args.type and args.status):
                print("❌ progress requires --type, --status, and --update or --name.")
            else:
                update_progress(db, target_name, args.type, args.status)

        case "kata":
            if not (args.name and args.language):
                print("❌ kata requires --name and --language.")
            else:
                handle_kata(args.name, args.language, args.file, args.answer, args.edit)

    db.close()

if __name__ == "__main__":
    main()
