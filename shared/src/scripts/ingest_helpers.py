import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "../data"


def load_yaml(filename):
    with open(DATA_DIR / filename, "r") as f:
        return yaml.safe_load(f)
