#[path = "answers.rs"]
mod answers;

#[test]
fn hello() {
    assert_eq!(answers::greeting(), "Hello, World!");
}
