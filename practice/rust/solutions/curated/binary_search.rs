pub fn binary_search(target: i32, arr: &[i32]) -> bool {
    let (mut low, mut high) = (0, arr.len());
    while low < high {
        let middle = low + (high - low) / 2;
        match arr[middle].cmp(&target) {
            std::cmp::Ordering::Equal => return true,
            std::cmp::Ordering::Less => low = middle + 1,
            std::cmp::Ordering::Greater => high = middle,
        }
    }
    false
}
