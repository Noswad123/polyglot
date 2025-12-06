import os
import subprocess
import tempfile
from .config import DEFAULT_EDITOR

def open_editor(initial_code: str = "", suffix: str = ".py") -> str:
    with tempfile.NamedTemporaryFile(suffix=suffix, mode="w+", delete=False) as tmp:
        tmp.write(initial_code)
        tmp.flush()
        subprocess.call([os.environ.get("EDITOR", DEFAULT_EDITOR), tmp.name])
        tmp.seek(0)
        result = tmp.read()
    os.unlink(tmp.name)
    return result
