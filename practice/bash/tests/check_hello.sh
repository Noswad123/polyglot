# Compatible with Bash 3.2. Keep completion state separate from learner stdout.
polyglot_load_stdout="$3"
{
    source "$1"
    polyglot_status=$?
    if [ "$polyglot_status" -ne 0 ]; then
        printf 'Source failed with status %s\n' "$polyglot_status" >&2
        printf 'failed\n' > "$2"
        exit 1
    fi
    if ! declare -F hello > /dev/null; then
        printf 'Expected a shell function named hello\n' >&2
        printf 'failed\n' > "$2"
        exit 1
    fi
    if [ -s "$polyglot_load_stdout" ]; then
        printf 'Source must not write stdout; put the greeting inside hello\n' >&2
        printf 'failed\n' > "$2"
        exit 1
    fi
    hello
    polyglot_status=$?
    if [ "$polyglot_status" -ne 0 ]; then
        printf 'hello failed with status %s\n' "$polyglot_status" >&2
        printf 'failed\n' > "$2"
        exit 1
    fi
} > "$3"
# Check before EXIT traps run, without a subshell or replacing stdout builtins.
IFS= read -r -d '' polyglot_stdout < "$3" || :
if [ "$polyglot_stdout" != $'Hello, World!\n' ]; then
    printf 'failed\n' > "$2"
    exit 1
fi
printf 'passed\n' > "$2"
