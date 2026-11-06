# Rust Users example

## Overview

Preserved, unverified Axum/SQLite project with its original `src/main.rs` nesting.
Its manifest declares a standalone workspace; it is not an active native binding
or part of the root CLI or Rust proof-exercise checks.

## API / Interfaces

`POST /users` and `POST /login` accept JSON `email` and `password` fields.
`GET /users?email=...` and `GET /users/{id}` fetch users. User responses use
`created_at`. `DB_PATH` defaults to `users.db`; `PORT` defaults to `8080`.

## Data Flow

Startup creates database parent directories if needed, opens/creates SQLite,
initializes the schema, and serves routes on `127.0.0.1:PORT`. Creation normalizes
email and stores a bcrypt hash; hashing and verification run in blocking tasks.

## Edge Cases

Running this project can create or modify a database and bind a port. Use
disposable data and credentials. Duplicate email creation returns a conflict;
invalid credentials return a bad request. Dependencies, compilation, and server
behavior have not been verified here. This is not a production authentication service.

## Example usage

For manual exploration only, after inspecting source and dependencies, from this
directory with a suitable Rust toolchain and dependencies available:

```sh
DB_PATH=/tmp/polyglot-rust-users-demo.db PORT=18081 cargo run
```

Choose a new disposable database path and unused port. Do not add dependencies
merely to validate native practice; the existing manifest owns this project's setup.

## Related files

- [Source and local request/response types](src/main.rs), [manifest](Cargo.toml)
- [Users question draft](../../../../README/katas/users.md)
- [Active Rust track](../../README.md), [inventory](../../../../README/katas/index.md)
- [Execution limits](../../../../README/exercises.md#collection-layout-and-execution-limits)
