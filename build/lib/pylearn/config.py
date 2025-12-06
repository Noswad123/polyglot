from pathlib import Path
import os
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")

DB_PATH = Path(os.getenv("POLYGLOT_DB_PATH", ROOT_DIR / "src" / "shared" / "db" / "polyglot.db"))
KATAS_DIR = Path(os.getenv("POLYGLOT_KATAS_PYTHON", ROOT_DIR / "src/python/katas"))

YAML_DIR = Path(os.environ.get("POLYGLOT_YAML_DIR", ROOT_DIR / "src" / "shared" / "yaml"))

DEFAULT_EDITOR = os.environ.get("POLYGLOT_DEFAULT_EDITOR", "nvim")
DEFAULT_LANGUAGE_NAME = "Python"
