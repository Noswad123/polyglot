pub fn fibonacci(length: usize) -> Vec<u32> {
    let mut terms = Vec::with_capacity(length);
    let (mut first, mut second) = (1, 1);
    for _ in 0..length {
        terms.push(first);
        (first, second) = (second, first + second);
    }
    terms
}
