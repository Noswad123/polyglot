pub fn length_of_last_word(text: &str) -> usize {
    text.split_whitespace().next_back().map_or(0, str::len)
}
