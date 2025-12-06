from pathlib import Path
import os

# Try to detect the project root by walking up until we find a pyproject.toml
_THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT: Path | None = None
for parent in _THIS_FILE.parents:
    if (parent / "pyproject.toml").exists():
        PROJECT_ROOT = parent
        break

# Fallback if we didn't find a pyproject (shouldn't happen in dev, but might in a tool install)
if PROJECT_ROOT is None:
    PROJECT_ROOT = _THIS_FILE.parents[3]

DEV_DB_DEFAULT = PROJECT_ROOT / "src" / "shared" / "db" / "polyglot.db"
DEV_KATAS_DEFAULT = PROJECT_ROOT / "src" / "python" / "katas"

DB_PATH = Path(os.environ.get("POLYGLOT_DB_PATH", DEV_DB_DEFAULT)).expanduser()
KATAS_DIR = Path(os.environ.get("POLYGLOT_KATAS_PYTHON", DEV_KATAS_DEFAULT)).expanduser()
DEFAULT_EDITOR = os.environ.get("POLYGLOT_DEFAULT_EDITOR", "nvim")
