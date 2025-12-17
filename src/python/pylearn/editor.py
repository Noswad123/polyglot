import os
import subprocess
import tempfile
from pathlib import Path
from .config import DEFAULT_EDITOR


def open_editor(initial_code: str = "", suffix: str = ".py") -> str:
    """
    Opens the editor with either:
    - the given text buffer (normal use), or
    - the contents of a file path (only if initial_code is a valid file path).

    Returns the edited text.
    """

    if (
        isinstance(initial_code, str)
        and "\n" not in initial_code
        and len(initial_code) < 100
        and Path(initial_code).exists()
        and Path(initial_code).is_file()
    ):
        content = Path(initial_code).read_text()
    else:
        content = initial_code

    # Now launch editor on a temp file
    with tempfile.NamedTemporaryFile(suffix=suffix, mode="w+", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        subprocess.call([os.environ.get("EDITOR", DEFAULT_EDITOR), tmp.name])
        tmp.seek(0)
        result = tmp.read()

    os.unlink(tmp.name)
    return result
