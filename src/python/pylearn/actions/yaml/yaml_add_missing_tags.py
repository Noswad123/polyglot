import sqlite3
from ...config import DB_PATH
from .yaml_helpers import load_yaml

def add_missing_tags_from_concepts() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    concepts = load_yaml("concepts.yaml") or []
    tag_set = set()

    for concept in concepts:
        tags = concept.get("tags") or []
        tag_set.update(tags)

    cur.execute("SELECT name FROM tags")
    existing = {row[0] for row in cur.fetchall()}

    missing = tag_set - existing
    if not missing:
        print("✅ All tags already exist in the database.")
        conn.close()
        return

    print(f"🔍 Found {len(missing)} missing tags...")
    for tag in sorted(missing):
        cur.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
        print(f"✅ Inserted tag: {tag}")

    conn.commit()
    conn.close()
    print("✅ Tag insertion complete.")
