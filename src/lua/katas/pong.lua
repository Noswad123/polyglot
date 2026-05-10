-- need to install luasockets as lua does not supprot TCP connections
-- out of the box
-- Run: PORT=8080 lua pong.lua

-- Q:
-- How would I know I needed luarocks and luasocket?

local socket = require("socket")

local port = tonumber(os.getenv("PORT")) or 8080

local server = assert(socket.bind("127.0.0.1", port))
server:settimeout(nil) -- block for new connections

print(("Listening on http://localhost:%d"):format(port))

while true do
  local client = server:accept()
  client:settimeout(2)

  -- Read request line: e.g. "GET /ping HTTP/1.1"
  local request_line = client:receive("*l")
  if not request_line then
    client:close()
    goto continue
  end

  -- Drain headers until empty line
  while true do
    local line = client:receive("*l")
    if not line or line == "" then break end
  end

  local method, path = request_line:match("^(%S+)%s+(%S+)%s+HTTP/%d%.%d")
  local body, status

  if method == "GET" and path == "/ping" then
    body = "pong"
    status = "200 OK"
  else
    body = "Not Found"
    status = "404 Not Found"
  end

  local response =
    ("HTTP/1.1 %s\r\n"):format(status) ..
    "Content-Type: text/plain\r\n" ..
    ("Content-Length: %d\r\n"):format(#body) ..
    "Connection: close\r\n" ..
    "\r\n" ..
    body

  client:send(response)
  client:close()

  ::continue::
end
