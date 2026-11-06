# Go Users example

## Overview

Preserved, unverified HTTP/SQLite project, not a native Polyglot binding.
The existing module and dependency files are retained; do not initialize a new module.

## API / Interfaces

`POST /users` and `POST /login` take JSON `email` and `password` fields.
`GET /users?email=...` and `GET /users/{id}` fetch users. Responses use `createdAt`.
`DB_PATH` defaults to `users.db`; `PORT` defaults to `8080`.

## Data Flow

`main.go` opens SQLite, initializes the users schema, and dispatches HTTP requests.
Creation normalizes email and stores a bcrypt password hash; login compares the hash.

## Edge Cases

This example creates or modifies a database and binds `:PORT`, not just loopback.
Use disposable data and credentials in an isolated environment. Duplicate email
creation returns a conflict; invalid login returns unauthorized. Compilation,
dependencies, and server behavior have not been verified for this layout.

## Example usage

For manual exploration only, after reviewing source and dependencies, from this
directory with a suitable Go toolchain and dependencies available:

```sh
DB_PATH=/tmp/polyglot-go-users-demo.db PORT=18080 go run .
```

Choose a new disposable database path and unused port; this is not a test command.

## Related files

- [Source](main.go), [module](go.mod), [dependency checksums](go.sum)
- [Users question draft](../../../README/katas/users.md)
- [Inventory](../../../README/katas/index.md), [execution limits](../../../README/exercises.md#collection-layout-and-execution-limits)
