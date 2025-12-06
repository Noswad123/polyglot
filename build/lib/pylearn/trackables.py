from .db import get_connection

def list_items(item_type: str) -> None:
    with get_connection() as db:
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

def update_progress(name: str, item_type: str, status: str, notes: str | None = None):
    if status not in ("not started", "in progress", "mastered", "abandoned"):
        print(f"❌ Invalid status: {status}")
        return

    with get_connection() as db:
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
    print(f"✅ Updated {item_type} '{name}' to status '{status}'.")

def show_status(item_type: str | None = None):
    query = """
        SELECT t.type, t.name, COALESCE(p.status, 'not started') AS status
        FROM trackables t
        LEFT JOIN trackable_progress p ON p.trackable_id = t.id
    """
    params: list[str] = []
    if item_type:
        query += " WHERE t.type = ?"
        params.append(item_type)
    query += " ORDER BY t.type, t.name"

    with get_connection() as db:
        rows = db.execute(query, tuple(params)).fetchall()

    if not rows:
        print("No trackables found.")
        return

    for ttype, name, status in rows:
        print(f"[{ttype}] {name}: {status}")
