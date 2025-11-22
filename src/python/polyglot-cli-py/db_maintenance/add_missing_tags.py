import sqlite3
import yaml
from pathlib import Path

"""
Adds missing tags to db
"""
DB_PATH = Path(__file__).resolve().parent / "../../db/programming_languages.db"
CONCEPTS_FILE = Path(__file__).resolve().parent / "../data/concepts.yaml"


def extract_unique_tags(concepts):
    tag_set = set()
    for concept in concepts:
        if concept.get("tags"):
            tag_set.update(concept["tags"])
    return tag_set


def load_concepts_yaml():
    with open(CONCEPTS_FILE, "r") as f:
        return yaml.safe_load(f)


def get_existing_tags(cur):
    cur.execute("SELECT name FROM tags")
    return set(row[0] for row in cur.fetchall())


def insert_missing_tags(cur, tags_to_insert):
    for tag in sorted(tags_to_insert):
        cur.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
        print(f"✅ Inserted tag: {tag}")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    concepts = load_concepts_yaml()
    yaml_tags = extract_unique_tags(concepts)
    db_tags = get_existing_tags(cur)

    missing_tags = yaml_tags - db_tags
    if not missing_tags:
        print("✅ All tags already exist in the database.")
    else:
        print(f"🔍 Found {len(missing_tags)} missing tags...")
        insert_missing_tags(cur, missing_tags)
        conn.commit()
        print("✅ Tag insertion complete.")

    conn.close()


if __name__ == "__main__":
    main()
