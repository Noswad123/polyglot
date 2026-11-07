#[path = "exercises/hello.rs"]
mod exercise;

const FUNCTION: fn() -> &'static str = exercise::greeting; // polyglot:api

#[test]
fn hello() {
    assert_eq!(FUNCTION(), "Hello, World!");
}
