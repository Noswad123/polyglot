#[path = "../exercises/length_of_last_word.rs"]
mod exercise;

const FUNCTION: fn(&str) -> usize = exercise::length_of_last_word; // polyglot:api

#[test]
fn length_of_last_word() {
    let long = "x".repeat(300);
    let cases = [
        ("Hello World", 5),
        ("   fly me   to   the moon  ", 4),
        ("single", 6),
        ("", 0),
        ("   ", 0),
        (" \t\n", 0),
        ("hello\tworld", 5),
        ("hello\nworld\n", 5),
        ("hello world!", 6),
        ("hello\rworld\r", 5),
        ("hello\u{000b}world\u{000c}", 5),
        (" \t\n\r\u{000b}\u{000c}", 0),
        (long.as_str(), 300),
    ];
    for (text, expected) in cases {
        let result = FUNCTION(text);
        assert_eq!(
            result, expected,
            "text: {text:?}\nYour result: {result:?}\nExpected result: {expected:?}"
        );
    }
}
