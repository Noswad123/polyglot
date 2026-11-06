#!/bin/sh
# Explicit opt-in installation; never changes core.hooksPath or replaces a hook.
set -eu

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_OBJECT_DIRECTORY \
    GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_IMPLICIT_WORK_TREE \
    GIT_SHALLOW_FILE GIT_CONFIG GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS
export GIT_OPTIONAL_LOCKS=0

root=$(git rev-parse --show-toplevel)
if configured=$(git -C "$root" config --get core.hooksPath); then
    printf '%s\n' \
        "Polyglot: core.hooksPath is already configured ($configured)." \
        'Integrate the guard with your existing hook setup; nothing was replaced.' >&2
    exit 1
else
    status=$?
    if [ "$status" -ne 1 ]; then
        printf '%s\n' 'Polyglot: could not inspect hook configuration.' >&2
        exit 1
    fi
fi

source="$root/.githooks/pre-commit"
[ -f "$source" ] && [ -r "$source" ] || {
    printf '%s\n' "Polyglot: guard source is missing: $source" >&2
    exit 1
}
hook=$(git -C "$root" rev-parse --git-path hooks/pre-commit)
case "$hook" in
    /*) ;;
    *) hook="$root/$hook" ;;
esac

if [ -e "$hook" ] || [ -L "$hook" ]; then
    if [ ! -L "$hook" ] && [ -f "$hook" ] && cmp -s "$source" "$hook"; then
        chmod 0755 "$hook"
        printf '%s\n' "Polyglot: guard already installed at $hook"
        exit 0
    fi
    printf '%s\n' \
        "Polyglot: an existing pre-commit hook is present at $hook." \
        'Integrate the guard manually; nothing was replaced.' >&2
    exit 1
fi

install -d "$(dirname "$hook")"
install -m 0755 "$source" "$hook"
printf '%s\n' "Polyglot: installed main exercise guard at $hook"
