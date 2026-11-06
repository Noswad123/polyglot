#!/usr/bin/env bash
# pong.sh — one-file bash HTTP server
# Responds "pong" to GET /ping
# PORT defaults to 8080

set -euo pipefail

PORT="${PORT:-8080}"

# Portable mktemp (BSD + GNU)
HANDLER="$(mktemp -t pong_handler)"
cat > "$HANDLER" <<'EOF'
#!/usr/bin/env bash

# Read request line
IFS=$'\r\n'
read -r request_line || exit 0

# Drain headers
while IFS=$'\r\n' read -r line && [ -n "$line" ]; do :; done

path=$(printf '%s\n' "$request_line" | awk '{print $2}')

if [ "$path" = "/ping" ]; then
  body="pong"
  status="200 OK"
else
  body="Not Found"
  status="404 Not Found"
fi

printf 'HTTP/1.1 %s\r\n' "$status"
printf 'Content-Type: text/plain\r\n'
printf 'Content-Length: %d\r\n' "${#body}"
printf 'Connection: close\r\n'
printf '\r\n'
printf '%s' "$body"
EOF

chmod +x "$HANDLER"

cleanup() {
  rm -f "$HANDLER"
}
trap cleanup EXIT

echo "Listening on http://localhost:$PORT"

if command -v socat >/dev/null 2>&1; then
  exec socat TCP-LISTEN:"$PORT",reuseaddr,fork EXEC:"/bin/bash $HANDLER"
elif command -v ncat >/dev/null 2>&1; then
  exec ncat -lk "$PORT" -c "/bin/bash $HANDLER"
elif command -v nc >/dev/null 2>&1 && nc -h 2>&1 | grep -q '\-e'; then
  while true; do
    nc -l "$PORT" -e /bin/bash "$HANDLER"
  done
else
  echo "Error: install socat or ncat (recommended)." >&2
  exit 1
fi
