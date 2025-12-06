from .db import get_connection

def show_concept(concept_name: str, language: str | None = None):
    """
    Show examples from examples(language_id, concept_id) for a given concept,
    optionally filtered by language.
    """
    params: list[str] = [concept_name]
    query = """
        SELECT l.name AS language_name,
               c.name AS concept_name,
               e.code_snippet,
               e.explanation
        FROM examples e
        JOIN languages l ON l.id = e.language_id
        JOIN concepts c ON c.id = e.concept_id
        WHERE c.name = ?
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
