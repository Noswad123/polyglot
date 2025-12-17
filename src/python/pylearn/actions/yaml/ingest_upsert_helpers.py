import sqlite3
from typing import Any, Dict, List, Iterable, Optional


def upsert_trackable(
    cur: sqlite3.Cursor,
    *,
    name: str,
    trackable_type: str,
    description: str | None = None,
) -> Optional[int]:
    """
    Create or update a trackable and return its id.
    """
    cur.execute(
        "SELECT id FROM trackables WHERE name = ? AND type = ?",
        (name, trackable_type),
    )
    row = cur.fetchone()
    trackable_id = row[0] if row else None

    if trackable_id is None:
        cur.execute(
            """
            INSERT INTO trackables (name, type, description)
            VALUES (?, ?, ?)
            """,
            (name, trackable_type, description),
        )
        trackable_id = cur.lastrowid
    else:
        cur.execute(
            """
            UPDATE trackables
            SET name = ?, description = ?
            WHERE id = ? AND type = ?
            """,
            (name, description, trackable_id, trackable_type),
        )

    return trackable_id


def upsert_trackable_tags(
    cur: sqlite3.Cursor,
    trackable_id: int,
    tags: Iterable[str] | None,
) -> None:
    if not tags:
        return

    for tag in tags:
        cur.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
        cur.execute("SELECT id FROM tags WHERE name = ?", (tag,))
        tag_id = cur.fetchone()[0]
        cur.execute(
            """
            INSERT OR IGNORE INTO trackable_tags (trackable_id, tag_id)
            VALUES (?, ?)
            """,
            (trackable_id, tag_id),
        )


def upsert_trackable_progress(
    cur: sqlite3.Cursor,
    trackable_id: int,
    status: str | None,
    notes: str | None,
) -> None:
    if status is None and notes is None:
        return

    cur.execute(
        """
        INSERT OR REPLACE INTO trackable_progress (trackable_id, status, notes)
        VALUES (?, ?, ?)
        """,
        (trackable_id, status or "not started", notes),
    )

def upsert_language(cur: sqlite3.Cursor, lang: Dict[str, Any]) -> None:
    name = lang["name"]

    trackable_id = upsert_trackable(
        cur,
        name=name,
        trackable_type="language",
        description=lang.get("description"),
    )

    # language_info
    cur.execute(
        """
        INSERT OR REPLACE INTO language_info (trackable_id, version, documentation_url)
        VALUES (?, ?, ?)
        """,
        (
            trackable_id,
            lang.get("version"),
            lang.get("documentation_url"),
        ),
    )
    if trackable_id:
        upsert_trackable_tags(cur, trackable_id, lang.get("tags"))
        upsert_trackable_progress(cur, trackable_id, lang.get("status"), lang.get("notes"))

def upsert_concept(cur: sqlite3.Cursor, concept: Dict[str, Any]) -> None:
    name = concept["name"]
    trackable_type = concept.get("type", "concept")  # "concept" or "kata"

    trackable_id = upsert_trackable(
        cur,
        name=name,
        trackable_type=trackable_type,
        description=concept.get("description"),
    )

    if trackable_id:
        upsert_trackable_tags(cur, trackable_id, concept.get("tags"))
        upsert_trackable_progress(
            cur,
            trackable_id,
            concept.get("status"),
            concept.get("notes"),
        )

def upsert_kata(cur: sqlite3.Cursor, kata: Dict[str, Any]) -> None:
    trackable_id = upsert_trackable(
        cur,
        name=kata["name"],
        trackable_type="kata",
        description=kata.get("description"),
    )

    if trackable_id:
        upsert_trackable_tags(cur, trackable_id, kata.get("tags"))
        upsert_trackable_progress(
            cur,
            trackable_id,
            kata.get("status"),
            kata.get("notes"),
        )

def upsert_example(cur: sqlite3.Cursor, example: Dict[str, Any]) -> None:
    language_name = example["language"]
    concept_name = example["concept"]

    cur.execute(
        """
        SELECT id FROM trackables
        WHERE name = ? AND type = 'language'
        """,
        (language_name,),
    )
    lang_row = cur.fetchone()
    if not lang_row:
        print(f"⚠️ Language trackable not found: {language_name}")
        return
    language_trackable_id = lang_row[0]

    cur.execute(
        """
        SELECT id FROM trackables
        WHERE name = ? AND type IN ('concept', 'kata')
        """,
        (concept_name,),
    )
    concept_row = cur.fetchone()
    if not concept_row:
        print(f"⚠️ Concept/kata trackable not found: {concept_name}")
        return
    concept_trackable_id = concept_row[0]

    cur.execute(
        """
        INSERT OR REPLACE INTO examples (
            id,
            language_trackable_id,
            concept_trackable_id,
            code_snippet,
            explanation
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            example.get("id"),
            language_trackable_id,
            concept_trackable_id,
            example["code_snippet"],
            example.get("explanation"),
        ),
    )

    example_id = example.get("id")
    if not example_id:
        cur.execute("SELECT last_insert_rowid()")
        example_id = cur.fetchone()[0]

    for tag in example.get("tags", []):
        cur.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
        cur.execute("SELECT id FROM tags WHERE name = ?", (tag,))
        tag_id = cur.fetchone()[0]
        cur.execute(
            """
            INSERT OR IGNORE INTO example_tags (example_id, tag_id)
            VALUES (?, ?)
            """,
            (example_id, tag_id),
        )

def upsert_relationships(cur: sqlite3.Cursor, relationships: List[Dict[str, Any]]) -> None:
    for r in relationships:
        cur.execute("SELECT id FROM trackables WHERE name = ?", (r["source_name"],))
        source = cur.fetchone()
        cur.execute("SELECT id FROM trackables WHERE name = ?", (r["target_name"],))
        target = cur.fetchone()

        if source and target:
            cur.execute(
                """
                INSERT OR IGNORE INTO trackable_relationships (source_id, target_id, relation)
                VALUES (?, ?, ?)
                """,
                (source[0], target[0], r["relation"]),
            )
        else:
            print(f"⚠️ Relationship skipped (missing trackable): {r}")
