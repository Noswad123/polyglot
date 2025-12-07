import os
import re
import shutil
import sqlite3
from .config import DB_PATH, PROJECT_ROOT

LEETCODE_DIR = PROJECT_ROOT / "leetcode"
KATAS_DIR = PROJECT_ROOT / "katas"  # or src/python/katas if that’s where they ended up

def to_camel_case(name: str) -> str:
    words = re.split(r"[-_]", name)
    return words[0].lower() + "".join(w.capitalize() for w in words[1:])

def ensure_tag(conn, tag_name):
    cursor = conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    conn.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
    conn.commit()
    return conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,)).fetchone()[0]

def insert_kata(conn, name, description=""):
    cursor = conn.execute(
        "SELECT id FROM trackables WHERE name = ? AND type = 'kata'", (name,)
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    conn.execute(
        "INSERT INTO trackables (name, type, description) VALUES (?, 'kata', ?)",
        (name, description),
    )
    conn.commit()
    return conn.execute(
        "SELECT id FROM trackables WHERE name = ? AND type = 'kata'", (name,)
    ).fetchone()[0]

def tag_trackable(conn, trackable_id, tag_id):
    exists = conn.execute(
        "SELECT 1 FROM trackable_tags WHERE trackable_id = ? AND tag_id = ?",
        (trackable_id, tag_id),
    ).fetchone()
    if not exists:
        conn.execute(
            "INSERT INTO trackable_tags (trackable_id, tag_id) VALUES (?, ?)",
            (trackable_id, tag_id),
        )
        conn.commit()

def migrate_leetcode_problems():
    conn = sqlite3.connect(DB_PATH)
    leetcode_tag_id = ensure_tag(conn, "leetcode")

    for item in os.listdir(LEETCODE_DIR):
        src_path = LEETCODE_DIR / item
        if not src_path.is_dir():
            continue

        camel_case_name = to_camel_case(item)
        dst_path = KATAS_DIR / camel_case_name

        if dst_path.exists():
            print(f"⚠️ Skipping {item}: {dst_path} already exists")
            continue

        print(f"🚚 Moving {item} → {camel_case_name}")
        shutil.move(str(src_path), str(dst_path))

        for filename in os.listdir(dst_path):
            old_file_path = dst_path / filename
            base, ext = os.path.splitext(filename)
            camel_file_name = to_camel_case(base) + ext
            new_file_path = dst_path / camel_file_name
            os.rename(old_file_path, new_file_path)

        trackable_id = insert_kata(conn, camel_case_name)
        tag_trackable(conn, trackable_id, leetcode_tag_id)

    conn.close()
    print("✅ Migration complete.")
