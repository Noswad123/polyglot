from ..db import get_connection

def show_concept(concept_name: str, language: str | None = None):
    """
    Show examples for a given concept or kata trackable, optionally filtered by language.

    Uses examples.language_trackable_id / concept_trackable_id joined to trackables.
    """
    params: list[str] = [concept_name]

    query = """
        SELECT
            l.name AS language_name,
            c.name AS concept_name,
            e.code_snippet,
            e.explanation
        FROM examples e
        JOIN trackables AS l
          ON l.id = e.language_trackable_id
        JOIN trackables AS c
          ON c.id = e.concept_trackable_id
        WHERE c.name = ?
          AND l.type = 'language'
          AND c.type IN ('concept', 'kata')
    """

    if language:
        query += " AND l.name = ?"
        params.append(language)

    query += " ORDER BY l.name"

    with get_connection() as db:
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
