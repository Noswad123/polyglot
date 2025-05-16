from ingest_helpers import load_yaml

VALID_STATUSES = {"not started", "in progress", "mastered", "abandoned"}
VALID_RELATIONS = {"uses", "includes", "depends_on", "implements"}


def validate_example(cur, example):
    missing = []
    for field in ["language", "concept", "code_snippet"]:
        if field not in example:
            missing.append(field)
    if missing:
        return f"Missing fields in example: {', '.join(missing)}"

    cur.execute("SELECT 1 FROM languages WHERE name = ?",
                (example["language"],))
    if not cur.fetchone():
        return f"Unknown language in example: {example['language']}"

    cur.execute("SELECT 1 FROM concepts WHERE name = ?", (example["concept"],))
    if not cur.fetchone():
        return f"Unknown concept in example: {example['concept']}"
    return None


def validate_language(cur, lang):
    if "name" not in lang:
        return f"Missing 'id' or 'name' in language: {lang}"
    return None


def validate_concept(cur, concept):
    if "name" not in concept:
        return f"Missing 'id' or 'name' in concept: {concept}"
    if "status" in concept and concept["status"] not in VALID_STATUSES:
        return f"Invalid status '{concept['status']}' in concept '{concept['name']}'"
    return None


def validate_relationship(r):
    if "relation" not in r or r["relation"] not in VALID_RELATIONS:
        return f"Invalid or missing relation: {r}"
    if "source_name" not in r or "target_name" not in r:
        return f"Missing source or target name: {r}"
    return None


def validate_all(cur):
    errors = []

    for lang in load_yaml("languages.yaml"):
        err = validate_language(cur, lang)
        if err:
            errors.append(err)

    for concept in load_yaml("concepts.yaml"):
        err = validate_concept(cur, concept)
        if err:
            errors.append(err)

    for example in load_yaml("examples.yaml"):
        err = validate_example(cur, example)
        if err:
            errors.append(err)

    for rel in load_yaml("trackable_relationships.yaml"):
        err = validate_relationship(rel)
        if err:
            errors.append(err)

    return errors
