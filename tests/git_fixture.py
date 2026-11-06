"""Git subprocess isolation shared by disposable repository fixtures."""

import os


def isolated_git_env():
    """Keep tool discovery/HOME, but never inherit Git context or user config."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    return env
