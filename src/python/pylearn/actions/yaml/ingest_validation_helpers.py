from typing import Any, Dict, List
from .yaml_helpers import load_yaml

VALID_STATUSES = {"not started", "in progress", "mastered", "abandoned"}
VALID_RELATIONS = {"uses", "includes", "depends_on", "implements"}

def validate_example(example: Dict[str, Any]) -> str | None:
    """
    Validate example shape only (required fields, tag types).

    We do NOT hit the DB here anymore because:
    - legacy `languages` / `concepts` tables are gone
    - trackable existence is enforced later by upsert_example
    """
    missing = []
    for field in ["language", "concept", "code_snippet"]:
        if field not in example:
            missing.append(field)
    if missing:
        return f"Missing fields in example: {', '.join(missing)}"

    # tags validation (type only)
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

    return None

def validate_language(lang: Dict[str, Any]) -> str | None:
    if "name" not in lang:
        return f"Missing 'name' in language: {lang}"
    return None


def validate_concept(concept: Dict[str, Any]) -> str | None:
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


def validate_kata(kata: Dict[str, Any]) -> str | None:
    if "name" not in kata:
        return f"Missing 'name' in kata: {kata}"
    if "status" in kata and kata["status"] not in VALID_STATUSES:
        return f"Invalid status '{kata['status']}' in kata '{kata['name']}'"
    # optional: validate that 'concepts' is a list of strings
    concepts = kata.get("concepts")
    if concepts is not None:
        if not isinstance(concepts, list) or not all(isinstance(c, str) for c in concepts):
            return f"'concepts' must be a list of strings in kata '{kata['name']}'"
    return None

VALIDATOR_MAP = {
    "example": {
        "func": validate_example,
        "path": "examples.yaml",
    },
    "language": {
        "func": validate_language,
        "path": "languages.yaml",
    },
    "concept": {
        "func": validate_concept,
        "path": "concepts.yaml",
    },
    "kata": {
        "func": validate_kata,
        "path": "kata.yaml",
    },
    "relationship": {
        "func": validate_relationship,
        "path": "trackable_relationships.yaml",
    },
}

def validate_one(validator_name: str) -> List[str]:
    """
    Validate a single YAML file type (example, language, concept, relationship).
    Returns a list of error strings.
    """
    if validator_name not in VALIDATOR_MAP:
        raise ValueError(f"Unknown validator: {validator_name}")

    cfg = VALIDATOR_MAP[validator_name]
    items = load_yaml(cfg["path"]) or []
    errors: List[str] = []

    for item in items:
        err = cfg["func"](item)  # type: ignore[arg-type]
        if err:
            errors.append(err)

    return errors

def validate_all() -> List[str]:
    """
    Validate all YAML files defined in VALIDATOR_MAP.
    Returns a combined list of error strings.
    """
    errors: List[str] = []

    order = ["language", "concept", "kata", "example", "relationship"]

    for name in order:
        cfg = VALIDATOR_MAP[name]
        items = load_yaml(cfg["path"]) or []
        for item in items:
            err = cfg["func"](item)
            if err:
                errors.append(err)

    return errors
