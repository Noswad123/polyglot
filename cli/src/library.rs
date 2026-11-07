use std::fmt;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum QuestionStatus {
    Curated,
    Draft,
    Missing,
}

impl fmt::Display for QuestionStatus {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(match self {
            Self::Curated => "curated",
            Self::Draft => "draft",
            Self::Missing => "missing",
        })
    }
}

pub struct Reference {
    pub language: &'static str,
    pub path: &'static str,
    pub note: Option<&'static str>,
}

pub struct Problem {
    pub id: &'static str,
    pub title: &'static str,
    pub question_status: QuestionStatus,
    pub question_doc: Option<&'static str>,
    pub references: &'static [Reference],
}

macro_rules! document {
    () => {
        None
    };
    ($file:literal) => {
        Some(concat!("README/katas/", $file))
    };
}

macro_rules! implementation_root {
    (python) => {
        "practice/python/soutions"
    };
    (rust) => {
        "practice/rust/solutions"
    };
    (typescript) => {
        "practice/typescript"
    };
    (javascript) => {
        "practice/javascript"
    };
    (go) => {
        "practice/go"
    };
    (bash) => {
        "practice/bash"
    };
    (lua) => {
        "practice/lua"
    };
    (lisp) => {
        "practice/lisp"
    };
}

macro_rules! reference {
    ($language:ident, $file:literal) => {
        Reference {
            language: stringify!($language),
            path: concat!(implementation_root!($language), "/", $file),
            note: None,
        }
    };
    ($language:ident, $file:literal, $note:literal) => {
        Reference {
            note: Some($note),
            ..reference!($language, $file)
        }
    };
}

// Legacy solution attempts are not certified; curated examples carry check notes.
// `references` remains the JSON field name for export compatibility.
macro_rules! library {
    ($($name:ident: $id:literal, $title:literal, $status:ident, [$($doc:literal)?],
       [$(($language:ident, $file:literal $(, $note:literal)?)),*];)*) => {
        $(pub static $name: Problem = Problem {
            id: $id,
            title: $title,
            question_status: QuestionStatus::$status,
            question_doc: document!($($doc)?),
            references: &[$(reference!($language, $file $(, $note)?)),*],
        };)*
        pub static PROBLEMS: &[&Problem] = &[$(&$name),*];
    };
}

library! {
    BEST_TIME_TO_BUY_AND_SELL_STOCK: "best-time-to-buy-and-sell-stock", "Best Time to Buy and Sell Stock", Missing, [],
        [(typescript, "bestTimeToBuyAndSellStock.ts")];
    BINARY_SEARCH: "binary-search", "Binary Search", Curated, ["binarySearch.md"],
        [(python, "binary_search.py"),
         (python, "curated/binary_search.py", "Example checked against current native tests; not a proof of all behavior."),
         (rust, "curated/binary_search.rs", "Example checked against current native tests; not a proof of all behavior.")];
    BOGGLE: "boggle", "Boggle", Draft, ["boggle.md"],
        [(python, "boggle.py"), (typescript, "boggle.ts")];
    CANDY: "candy", "Candy", Missing, [],
        [(python, "candy.py"), (typescript, "candy.ts")];
    CONTAINER_WITH_MOST_WATER: "container-with-most-water", "Container With Most Water", Missing, [],
        [(python, "container_with_most_water.py")];
    FIBONACCI: "fibonacci", "Fibonacci", Curated, ["fibonacci.md"],
        [(python, "fibonacci.py"), (javascript, "fibonacci.js"),
         (python, "curated/fibonacci.py", "Example checked against current native tests; not a proof of all behavior."),
         (rust, "curated/fibonacci.rs", "Example checked against current native tests; not a proof of all behavior.")];
    FIND_IN_STRING: "find-in-string", "Find in String", Curated, ["find_in_string.md"],
        [(python, "find_in_string.py"), (typescript, "findTheIndexOfTheFirstOccurrenceInAString.ts"),
         (python, "curated/find_in_string.py", "Example checked against current native tests; not a proof of all behavior."),
         (rust, "curated/find_in_string.rs", "Example checked against current native tests; not a proof of all behavior.")];
    FIND_PIVOT_INDEX: "find-pivot-index", "Find Pivot Index", Missing, [],
        [(python, "find_pivot_index.py", "Empty placeholder; not implemented."), (typescript, "findPivotIndex.ts")];
    GAS_STATION: "gas-station", "Gas Station", Missing, [],
        [(typescript, "gasStation.ts")];
    H_INDEX: "h-index", "H-Index", Missing, [],
        [(typescript, "hIndex.ts")];
    HELLO_WORLD: "hello-world", "Hello, World!", Curated, ["hello_world.md"],
        [(python, "hello_world.py"), (javascript, "helloWorld.js"), (go, "helloWorld.go"),
         (bash, "hello_world.sh"), (lua, "helloWorld.lua"), (lisp, "hello-world.lisp"),
         (python, "curated/hello_world.py", "Example checked against current native tests; not a proof of all behavior."),
         (rust, "curated/hello_world.rs", "Example checked against current native tests; not a proof of all behavior."),
         (typescript, "solutions/curated/hello_world.ts", "Example checked against current native tests; not a proof of all behavior."),
         (go, "solutions/curated/hello_world.go", "Example checked against current native tests; not a proof of all behavior."),
         (bash, "solutions/curated/hello_world.sh", "Example checked against current native tests; not a proof of all behavior."),
         (lua, "solutions/curated/hello_world.lua", "Example checked against current native tests; not a proof of all behavior.")];
    INSERT_DELETE_GET_RANDOM: "insert-delete-get-random", "Insert Delete GetRandom", Missing, [],
        [(typescript, "insertDeleteGetRandom.ts")];
    INTEGER_TO_ROMAN: "integer-to-roman", "Integer to Roman", Draft, ["integer_to_Roman.md"],
        [(python, "integer_to_roman.py"), (typescript, "integerToRoman.ts")];
    IS_SUBSEQUENCE: "is-subsequence", "Is Subsequence", Draft, ["isSubsequence.md"],
        [(python, "is_subsequence.py"), (typescript, "isSubsequence.ts")];
    JUMP_GAME: "jump-game", "Jump Game", Missing, [],
        [(typescript, "jumpGame.ts")];
    LENGTH_OF_LAST_WORD: "length-of-last-word", "Length of Last Word", Curated, ["lengthOfLastWord.md"],
        [(python, "length_of_last_word.py"), (typescript, "lengthOfLastWord.ts"),
         (python, "curated/length_of_last_word.py", "Example checked against current native tests; not a proof of all behavior."),
         (rust, "curated/length_of_last_word.rs", "Example checked against current native tests; not a proof of all behavior.")];
    LONGEST_COMMON_PREFIX: "longest-common-prefix", "Longest Common Prefix", Missing, [],
        [(typescript, "longestCommonPrefix.ts")];
    MAJORITY_ELEMENT: "majority-element", "Majority Element", Draft, ["majorityElement.md"],
        [(python, "majority_element.py"), (typescript, "majorityElement.ts")];
    MERGE_SORTED_ARRAY: "merge-sorted-array", "Merge Sorted Array", Draft, ["MergeSortedArray.md"],
        [(python, "merge_sorted_array.py"), (typescript, "mergeSortedArray.ts")];
    PONG: "pong", "Pong / HTTP Ping", Draft, ["pong.md"],
        [(python, "pong.py"), (javascript, "pong.js"), (go, "pong.go"), (bash, "pong.sh"), (lua, "pong.lua")];
    PRODUCT_OF_ARRAY_EXCEPT_SELF: "product-of-array-except-self", "Product of Array Except Self", Draft, ["productOfArray.md"],
        [(python, "product_of_array_except_self.py"), (typescript, "productOfArrayExceptSelf.ts")];
    QUEUE: "queue", "Queue", Missing, [],
        [(python, "queue.py")];
    REMOVE_DUPLICATES_FROM_SORTED_ARRAY: "remove-duplicates-from-sorted-array", "Remove Duplicates from Sorted Array", Missing, [],
        [(typescript, "removeDuplicatesFromSortedArray.ts")];
    REMOVE_ELEMENT: "remove-element", "Remove Element", Missing, [],
        [(typescript, "removeElement.ts")];
    REVERSE_WORDS_IN_A_STRING: "reverse-words-in-a-string", "Reverse Words in a String", Draft, ["reverseWordsInAString.md"],
        [(python, "reverse_words_in_a_string.py"), (typescript, "reverseWordsInAString.ts")];
    ROMAN_TO_INTEGER: "roman-to-integer", "Roman to Integer", Draft, ["romanToInteger.md"],
        [(python, "roman_to_integer.py"), (typescript, "romanToInteger.ts")];
    ROTATE_ARRAY: "rotate-array", "Rotate Array", Draft, ["rotateArray.md"],
        [(python, "rotate_array.py"), (typescript, "roateArray.ts")];
    SCRABBLE: "scrabble", "Scrabble", Draft, ["scrabble.md"],
        [(typescript, "scrabble.ts")];
    SPIRAL_MATRIX: "spiral-matrix", "Spiral Matrix", Draft, ["spiral_matrix_walk.md"], [];
    STACK: "stack", "Stack", Missing, [], [(python, "stack.py")];
    SUDOKU_VALIDATOR: "sudoku-validator", "Sudoku Validator", Draft, ["sudoku_validator.md"], [];
    TEXT_JUSTIFICATION: "text-justification", "Text Justification", Missing, [],
        [(typescript, "textJustification.ts")];
    TRAPPING_RAIN_WATER: "trapping-rain-water", "Trapping Rain Water", Missing, [],
        [(typescript, "trappingRainWater.ts")];
    TWO_SUM: "two-sum", "Two Sum", Missing, [], [(typescript, "twoSum.ts")];
    USERS: "users", "Users", Draft, ["users.md"],
        [(python, "users.py"), (go, "users/main.go"), (rust, "users/src/main.rs")];
    VALID_PALINDROME: "valid-palindrome", "Valid Palindrome", Draft, ["validPalindrome.md"],
        [(typescript, "validPalindrome.ts")];
    ZIGZAG_CONVERSION: "zigzag-conversion", "Zigzag Conversion", Missing, [],
        [(typescript, "zigzagConversion.ts")];
}
