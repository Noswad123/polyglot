pub fn find_in_string(string: &str, substring: &str) -> isize {
    string.find(substring).map_or(-1, |index| index as isize)
}
