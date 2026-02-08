
# Questions

Make a one-file HTTP server: GET /ping -> pong

user will run access the route:
- curl -i http://localhost:8080/ping

# Comparisons
## Out of the box
- Go: comes with net/http
- Python: comes with http.server, socket
- Node: comes with http, net
- Lua: has no standard TCP/HTP stack
## Performance
### Go
- net/http is stable, performant and feature complete
- concurrency is straightforward(goroutines, channels) and cheap
- deployment is super simple
- good performance without fighting the runtime too much
### Python
- fast iteration
 
# Learning
When you start a server in any language, you are asking for one of these layers:
- Raw sockets (TCP accept/read/write)
- HTTP parsing + response formatting
- routing, middleware, and framework ergonomics
