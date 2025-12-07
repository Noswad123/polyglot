import sqlite3
from .config import DB_PATH
from .yaml_helpers import load_yaml
from .ingest_validation_helpers import validate_all, validate_one
from .ingest_upsert_helpers import (
    upsert_language,
    upsert_concept,
    upsert_example,
    upsert_relationships,
)

def insert_missing_tags(cur, concepts):
    tag_set = set()
    for concept in concepts:
        for tag in concept.get("tags") or []:
            tag_set.add(tag)

    if not tag_set:
        return

    cur.execute("SELECT name FROM tags")
    existing = {row[0] for row in cur.fetchall()}
    missing = tag_set - existing

    for tag in sorted(missing):
        cur.execute("INSERT INTO tags (name) VALUES (?)", (tag,))
        print(f"✅ Added missing tag: {tag}")

def ingest_all():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("🔍 Validating data...")
    errors = validate_all(cur)
    if errors:
        print("❌ Validation failed. Fix the following issues:")
        for err in errors:
            print(f"  - {err}")
        conn.close()
        return
    print("✅ Validation passed. Proceeding with ingestion...\n")

    for lang in load_yaml("languages.yaml"):
        upsert_language(cur, lang)

    concepts = load_yaml("concepts.yaml")
    insert_missing_tags(cur, concepts)

    for concept in concepts:
        upsert_concept(cur, concept)

    validate_one("example", cur)
    for ex in load_yaml("examples.yaml"):
        upsert_example(cur, ex)

    upsert_relationships(cur, load_yaml("trackable_relationships.yaml"))

    conn.commit()
    conn.close()
    print("✅ Ingest complete.")
