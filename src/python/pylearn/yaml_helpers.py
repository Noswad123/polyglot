import yaml

from .config import YAML_DIR


def load_yaml(filename: str):
    path = YAML_DIR / filename
    with path.open("r") as f:
        return yaml.safe_load(f)


def write_yaml(filename: str, data):
    path = YAML_DIR / filename
    YAML_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)
