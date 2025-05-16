import sqlite3
import yaml
from pathlib import Path
import zipfile
import os
from datetime import date
import argparse

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "../../db/programming_languages.db"
DATA_DIR = BASE_DIR / "../data"
DATA_DIR.mkdir(exist_ok=True)


# List of files to include in the snapshot
FILES_TO_INCLUDE = [
    DATA_DIR / "concepts.yaml",
    DATA_DIR / "languages.yaml",
    DATA_DIR / "examples.yaml",
    DATA_DIR / "tags.yaml",
    DATA_DIR / "trackable_relationships.yaml",
]


def zip_files(files):
    # Output filename with today's date
    today_str = date.today().isoformat()
    zip_filename = f"snapshot-{today_str}.zip"

# Create the zip file
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filepath in FILES_TO_INCLUDE:
            if os.path.isfile(filepath):
                zipf.write(filepath)
                print(f"Added: {filepath}")
            else:
                print(f"Skipped (not found): {filepath}")

    print(f"\nSnapshot created: {zip_filename}")


def write_yaml(filename, data):
    with open(DATA_DIR / filename, "w") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)


def export_languages(cur):
    cur.execute("""
        SELECT
            t.id, t.name, t.description,
            li.version, li.documentation_url
        FROM trackables t
        JOIN language_info li ON t.id = li.trackable_id
        WHERE t.type = 'language'
    """)
    rows = cur.fetchall()
    languages = [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "version": row[3],
            "documentation_url": row[4],
        }
        for row in rows
    ]
    write_yaml("languages.yaml", languages)


def export_concepts(cur):
    cur.execute("""
        SELECT id, name, description
        FROM trackables
        WHERE type = 'concept'
    """)
    concepts = []
    for trackable_id, name, description in cur.fetchall():
        cur.execute("""
            SELECT tags.name
            FROM trackable_tags
            JOIN tags ON tags.id = trackable_tags.tag_id
            WHERE trackable_tags.trackable_id = ?
        """, (trackable_id,))
        tags = [row[0] for row in cur.fetchall()]

        cur.execute("""
            SELECT status, notes
            FROM trackable_progress
            WHERE trackable_id = ?
        """, (trackable_id,))
        progress = cur.fetchone() or ("not started", None)

        concepts.append({
            "id": trackable_id,
            "name": name,
            "description": description,
            "tags": tags or None,
            "status": progress[0],
            "notes": progress[1],
        })
    write_yaml("concepts.yaml", concepts)


def export_examples(cur):
    cur.execute("""
        SELECT
            e.id,
            l.name AS language,
            c.name AS concept,
            e.code_snippet,
            e.explanation
        FROM examples e
        JOIN languages l ON e.language_id = l.id
        JOIN concepts c ON e.concept_id = c.id
    """)
    examples = []
    rows = cur.fetchall()
    for row in rows:
        example_id, language, concept, code_snippet, explanation = row

        cur.execute("""
            SELECT tags.name
            FROM example_tags
            JOIN tags ON example_tags.tag_id = tags.id
            WHERE example_tags.example_id = ?
        """, (example_id,))

        tags = [r[0] for r in cur.fetchall()]

        example = {
            "id": example_id,
            "language": language,
            "concept": concept,
            "code_snippet": code_snippet,
            "explanation": explanation,
        }
        if tags:
            example["tags"] = tags

        examples.append(examples)
    write_yaml("examples.yaml", examples)


def export_trackable_relationships(cur):
    cur.execute("""
        SELECT
            src.id, src.name, tgt.id, tgt.name, r.relation
        FROM trackable_relationships r
        JOIN trackables src ON r.source_id = src.id
        JOIN trackables tgt ON r.target_id = tgt.id
    """)
    relationships = [
        {
            "source_id": row[0],
            "source_name": row[1],
            "target_id": row[2],
            "target_name": row[3],
            "relation": row[4],
        }
        for row in cur.fetchall()
    ]
    write_yaml("trackable_relationships.yaml", relationships)


def export_tags(cur):
    cur.execute("SELECT id, name FROM tags ORDER BY id")
    tags = [{"id": row[0], "name": row[1]} for row in cur.fetchall()]
    write_yaml("tags.yaml", tags)


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    export_languages(cur)
    export_concepts(cur)
    export_tags(cur)
    export_examples(cur)
    export_trackable_relationships(cur)

    conn.close()
    print("✅ Export complete. Files saved to 'data/' directory.")

    parser = argparse.ArgumentParser(
        description="Export data from the DB and optionally zip the result.")
    parser.add_argument("--zip", "-z", action="store_true",
                        help="Create a zip snapshot after export.")
    args = parser.parse_args()

    if args.zip:
        zip_files(FILES_TO_INCLUDE)


if __name__ == "__main__":
    main()
