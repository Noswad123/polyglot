#[path = "../exercises/find_in_string.rs"]
mod exercise;

const FUNCTION: fn(&str, &str) -> isize = exercise::find_in_string; // polyglot:api

#[test]
fn find_in_string() {
    let long = "x".repeat(300) + "end";
    let cases = [
        ("Dawson, Jamal", "Jamal", 8),
        ("banana", "ana", 1),
        ("abc", "a", 0),
        ("abc", "c", 2),
        ("abc", "abc", 0),
        ("abc", "z", -1),
        ("a", "abc", -1),
        ("abc", "A", -1),
        ("abc", "", 0),
        ("", "", 0),
        ("", "a", -1),
        (long.as_str(), "end", 300),
    ];
    for (string, substring, expected) in cases {
        let result = FUNCTION(string, substring);
        assert_eq!(result, expected,
            "string: {string:?}, substring: {substring:?}\nYour result: {result:?}\nExpected result: {expected:?}");
    }
}
