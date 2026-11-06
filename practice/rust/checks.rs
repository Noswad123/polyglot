#[path = "exercises/hello.rs"]
mod exercise;

#[test]
fn hello() {
    assert_eq!(exercise::greeting(), "Hello, World!");
}
