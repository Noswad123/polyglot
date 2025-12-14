import sqlite3
import zipfile
from datetime import date

from ..config import DB_PATH, YAML_DIR
from .yaml_helpers import write_yaml


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
        cur.execute(
            """
            SELECT tags.name
            FROM trackable_tags
            JOIN tags ON tags.id = trackable_tags.tag_id
            WHERE trackable_tags.trackable_id = ?
        """,
            (trackable_id,),
        )
        tags = [row[0] for row in cur.fetchall()]

        cur.execute(
            """
            SELECT status, notes
            FROM trackable_progress
            WHERE trackable_id = ?
        """,
            (trackable_id,),
        )
        progress = cur.fetchone() or ("not started", None)

        concepts.append(
            {
                "id": trackable_id,
                "name": name,
                "description": description,
                "tags": tags or None,
                "status": progress[0],
                "notes": progress[1],
            }
        )
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

        cur.execute(
            """
            SELECT tags.name
            FROM example_tags
            JOIN tags ON example_tags.tag_id = tags.id
            WHERE example_tags.example_id = ?
        """,
            (example_id,),
        )

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

        examples.append(example)
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


def export_all(zip_after: bool = False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    YAML_DIR.mkdir(parents=True, exist_ok=True)

    export_languages(cur)
    export_concepts(cur)
    export_tags(cur)
    export_examples(cur)
    export_trackable_relationships(cur)

    conn.close()
    print(f"✅ Export complete. Files saved to '{YAML_DIR}' directory.")

    if zip_after:
        zip_files()


def zip_files():
    today_str = date.today().isoformat()
    zip_filename = f"snapshot-{today_str}.zip"
    yaml_files = [
        YAML_DIR / "concepts.yaml",
        YAML_DIR / "languages.yaml",
        YAML_DIR / "examples.yaml",
        YAML_DIR / "tags.yaml",
        YAML_DIR / "trackable_relationships.yaml",
    ]

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for filepath in yaml_files:
            if filepath.is_file():
                zipf.write(filepath, arcname=filepath.name)
                print(f"Added: {filepath}")
            else:
                print(f"Skipped (not found): {filepath}")
    print(f"\nSnapshot created: {zip_filename}")
