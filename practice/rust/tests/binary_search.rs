#[path = "../exercises/binary_search.rs"]
mod exercise;

const FUNCTION: fn(i32, &[i32]) -> bool = exercise::binary_search; // polyglot:api

#[test]
fn binary_search() {
    // Behavioral checks do not prove the algorithm's complexity.
    let cases: &[(i32, &[i32], bool)] = &[
        (1, &[], false),
        (5, &[5], true),
        (4, &[5], false),
        (6, &[5], false),
        (-8, &[-8, -3, 0, 4, 9, 12], true),
        (12, &[-8, -3, 0, 4, 9, 12], true),
        (0, &[-8, -3, 0, 4, 9, 12], true),
        (-9, &[-8, -3, 0, 4, 9, 12], false),
        (13, &[-8, -3, 0, 4, 9, 12], false),
        (5, &[-8, -3, 0, 4, 9, 12], false),
        (2, &[1, 2, 2, 2, 3], true),
        (4, &[1, 2, 2, 2, 3], false),
        (7, &[7, 7, 7, 7], true),
        (6, &[7, 7, 7, 7], false),
        (1, &[1, 2], true),
        (2, &[1, 2], true),
        (i32::MIN, &[i32::MIN, 0, i32::MAX], true),
        (i32::MAX, &[i32::MIN, 0, i32::MAX], true),
    ];
    for &(target, arr, expected) in cases {
        let original = arr.to_vec();
        let result = FUNCTION(target, arr);
        assert_eq!(result, expected,
            "target: {target}, arr: {arr:?}\nYour result: {result:?}\nExpected result: {expected:?}");
        assert_eq!(
            arr, original,
            "input after call\nYour result: {arr:?}\nExpected result: {original:?}"
        );
    }
}
