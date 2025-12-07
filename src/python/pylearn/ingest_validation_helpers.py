from typing import Any, Dict, List
from .yaml_helpers import load_yaml

VALID_STATUSES = {"not started", "in progress", "mastered", "abandoned"}
VALID_RELATIONS = {"uses", "includes", "depends_on", "implements"}


def validate_example(cur, example: Dict[str, Any]) -> str | None:
    missing = []
    for field in ["language", "concept", "code_snippet"]:
        if field not in example:
            missing.append(field)
    if missing:
        return f"Missing fields in example: {', '.join(missing)}"

    cur.execute("SELECT 1 FROM languages WHERE name = ?", (example["language"],))
    if not cur.fetchone():
        return f"Unknown language in example: {example['language']}"

    cur.execute("SELECT 1 FROM concepts WHERE name = ?", (example["concept"],))
    if not cur.fetchone():
        return f"Unknown concept in example: {example['concept']}"

    # tags validation
    if "tags" in example:
        if not isinstance(example["tags"], list):
            return (
                f"'tags' must be a list in example: "
                f"'{example.get('title', example['code_snippet'])[:30]}'"
            )
        for tag in example["tags"]:
            if not isinstance(tag, str):
                return (
                    f"Each tag must be a string in example: "
                    f"'{example.get('title', example['code_snippet'])[:30]}'"
                )

        cur.execute("SELECT name FROM tags")
        known_tags = {row[0] for row in cur}
        unknown = [tag for tag in example.get("tags", []) if tag not in known_tags]
        if unknown:
            return f"Unknown tag(s) in example: {unknown}"

    return None


def validate_language(cur, lang: Dict[str, Any]) -> str | None:
    if "name" not in lang:
        return f"Missing 'name' in language: {lang}"
    return None


def validate_concept(cur, concept: Dict[str, Any]) -> str | None:
    if "name" not in concept:
        return f"Missing 'name' in concept: {concept}"
    if "status" in concept and concept["status"] not in VALID_STATUSES:
        return f"Invalid status '{concept['status']}' in concept '{concept['name']}'"
    return None


def validate_relationship(r: Dict[str, Any]) -> str | None:
    if "relation" not in r or r["relation"] not in VALID_RELATIONS:
        return f"Invalid or missing relation: {r}"
    if "source_name" not in r or "target_name" not in r:
        return f"Missing source or target name: {r}"
    return None


def validate_one(validator_name: str, cur) -> List[str]:
    """
    Validate a single YAML file type (example, language, concept, relationship).
    Returns a list of error strings.
    """
    validator_map = {
        "example": {
            "func": validate_example,
            "path": "examples.yaml",
            "needs_cur": True,
        },
        "language": {
            "func": validate_language,
            "path": "languages.yaml",
            "needs_cur": True,
        },
        "concept": {
            "func": validate_concept,
            "path": "concepts.yaml",
            "needs_cur": True,
        },
        "relationship": {
            "func": validate_relationship,
            "path": "trackable_relationships.yaml",
            "needs_cur": False,
        },
    }

    if validator_name not in validator_map:
        raise ValueError(f"Unknown validator: {validator_name}")

    cfg = validator_map[validator_name]
    items = load_yaml(cfg["path"]) or []
    errors: List[str] = []

    if cfg["needs_cur"]:
        for thing in items:
            err = cfg["func"](cur, thing)  # type: ignore[arg-type]
            if err:
                errors.append(err)
    else:
        for thing in items:
            err = cfg["func"](thing)  # type: ignore[arg-type]
            if err:
                errors.append(err)

    return errors


def validate_all(cur) -> List[str]:
    """
    Validate languages, concepts, (optionally examples), and relationships.
    Returns a list of error strings.
    """
    errors: List[str] = []

    for lang in load_yaml("languages.yaml") or []:
        err = validate_language(cur, lang)
        if err:
            errors.append(err)

    for concept in load_yaml("concepts.yaml") or []:
        err = validate_concept(cur, concept)
        if err:
            errors.append(err)

    for example in load_yaml("examples.yaml") or []:
        err = validate_example(cur, example)
        if err:
            errors.append(err)

    for rel in load_yaml("trackable_relationships.yaml") or []:
        err = validate_relationship(rel)
        if err:
            errors.append(err)

    return errors
