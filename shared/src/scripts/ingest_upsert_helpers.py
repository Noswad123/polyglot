
import sqlite3
from typing import Any, Dict, List


def upsert_language(cur: sqlite3.Cursor, lang: Dict[str, Any]) -> None:
    name = lang["name"]
    cur.execute(
        "SELECT id FROM trackables WHERE name = ? AND type = 'language'", (name,))
    row = cur.fetchone()
    lang_id = row[0] if row else None

    if lang_id is None:
        cur.execute("""
            INSERT INTO trackables (name, type, description)
            VALUES (?, 'language', ?)
        """, (name, lang.get("description")))
        lang_id = cur.lastrowid
    else:
        cur.execute("""
            UPDATE trackables
            SET name = ?, description = ?
            WHERE id = ? AND type = 'language'
        """, (name, lang.get("description"), lang_id))

    cur.execute("""
        INSERT OR IGNORE INTO languages (id, name, version, documentation_url, description)
        VALUES (?, ?, ?, ?, ?)
    """, (
        lang_id, name,
        lang.get("version"), lang.get("documentation_url"),
        lang.get("description")
    ))

    cur.execute("""
        UPDATE languages
        SET version = ?, documentation_url = ?, description = ?
        WHERE id = ?
    """, (
        lang.get("version"),
        lang.get("documentation_url"),
        lang.get("description"),
        lang_id
    ))

    cur.execute("""
        INSERT OR REPLACE INTO language_info (trackable_id, version, documentation_url)
        VALUES (?, ?, ?)
    """, (lang_id, lang.get("version"), lang.get("documentation_url")))


def upsert_concept(cur: sqlite3.Cursor, concept: Dict[str, Any]) -> None:
    name = concept["name"]
    cur.execute(
        "SELECT id FROM trackables WHERE name = ? AND type = 'concept'", (name,))
    row = cur.fetchone()
    concept_id = row[0] if row else None

    if concept_id is None:
        cur.execute("""
            INSERT INTO trackables (name, type, description)
            VALUES (?, 'concept', ?)
        """, (name, concept.get("description")))
        concept_id = cur.lastrowid
    else:
        cur.execute("""
            UPDATE trackables
            SET name = ?, description = ?
            WHERE id = ? AND type = 'concept'
        """, (name, concept.get("description"), concept_id))

    cur.execute("""
        INSERT OR IGNORE INTO concepts (id, name, description)
        VALUES (?, ?, ?)
    """, (concept_id, name, concept.get("description")))

    cur.execute("""
        UPDATE concepts
        SET name = ?, description = ?
        WHERE id = ?
    """, (name, concept.get("description"), concept_id))

    for tag in concept.get("tags", []):
        cur.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
        cur.execute("SELECT id FROM tags WHERE name = ?", (tag,))
        tag_id = cur.fetchone()[0]
        cur.execute("""
            INSERT OR IGNORE INTO trackable_tags (trackable_id, tag_id)
            VALUES (?, ?)
        """, (concept_id, tag_id))

    cur.execute("""
        INSERT OR REPLACE INTO trackable_progress (trackable_id, status, notes)
        VALUES (?, ?, ?)
    """, (concept_id, concept.get("status", "not started"), concept.get("notes")))


def upsert_example(cur: sqlite3.Cursor, example: Dict[str, Any]) -> None:
    cur.execute("SELECT id FROM languages WHERE name = ?",
                (example["language"],))
    lang_id = cur.fetchone()
    if not lang_id:
        print(f"⚠️ Language not found: {example['language']}")
        return
    lang_id = lang_id[0]

    cur.execute("SELECT id FROM concepts WHERE name = ?",
                (example["concept"],))
    concept_id = cur.fetchone()
    if not concept_id:
        print(f"⚠️ Concept not found: {example['concept']}")
        return
    concept_id = concept_id[0]

    cur.execute("""
        INSERT OR REPLACE INTO examples (id, language_id, concept_id, code_snippet, explanation)
        VALUES (?, ?, ?, ?, ?)
    """, (
        example.get("id"),
        lang_id,
        concept_id,
        example["code_snippet"],
        example.get("explanation")
    ))


def upsert_relationships(cur: sqlite3.Cursor, relationships: List[Dict[str, Any]]) -> None:
    for r in relationships:
        cur.execute("SELECT id FROM trackables WHERE name = ?",
                    (r["source_name"],))
        source_id = cur.fetchone()
        cur.execute("SELECT id FROM trackables WHERE name = ?",
                    (r["target_name"],))
        target_id = cur.fetchone()
        if source_id and target_id:
            cur.execute("""
                INSERT OR IGNORE INTO trackable_relationships (source_id, target_id, relation)
                VALUES (?, ?, ?)
            """, (source_id[0], target_id[0], r["relation"]))
        else:
            print(f"⚠️ Relationship skipped (missing trackable): {r}")
