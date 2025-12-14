from pathlib import Path
import os

_THIS_FILE = Path(__file__).resolve()

PROJECT_ROOT: Path | None = None
for parent in _THIS_FILE.parents:
    if (parent / "pyproject.toml").exists():
        PROJECT_ROOT = parent
        break
if PROJECT_ROOT is None:
    PROJECT_ROOT = _THIS_FILE.parents[3]

# Dev defaults
DEV_DB_DEFAULT         = PROJECT_ROOT / "src" / "shared" / "db" / "polyglot.db"
DEV_YAML_DIR_DEFAULT   = PROJECT_ROOT / "src" / "shared" / "yaml"
DEV_LANGUAGES_ROOT     = PROJECT_ROOT / "src" / "languages"      # adjust if needed
DEV_KATAS_DIR_DEFAULT  = PROJECT_ROOT / "src" / "python" / "katas"

DB_PATH        = Path(os.environ.get("POLYGLOT_DB_PATH", DEV_DB_DEFAULT)).expanduser()
YAML_DIR       = Path(os.environ.get("POLYGLOT_YAML_DIR", DEV_YAML_DIR_DEFAULT)).expanduser()
LANGUAGES_ROOT = Path(os.environ.get("POLYGLOT_LANGUAGES_ROOT", DEV_LANGUAGES_ROOT)).expanduser()
KATAS_DIR      = PROJECT_ROOT / "README" / "katas"
TESTS_DIR = PROJECT_ROOT / "src" / "python" / "tests" / "katas"
PYTHON_KATAS_DIR = PROJECT_ROOT / "src" / "python" / "katas"
DEFAULT_EDITOR = os.environ.get("POLYGLOT_DEFAULT_EDITOR", "vim")
