use std::fmt;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Language {
    Python,
    Rust,
}

impl Language {
    pub fn parse(value: &str) -> Option<Self> {
        match value {
            "python" => Some(Self::Python),
            "rust" => Some(Self::Rust),
            _ => None,
        }
    }

    pub fn workspace(self) -> Workspace {
        match self {
            Self::Python => Workspace {
                directory: "practice/python",
                starter: "starter.py",
                answers: "answers.py",
                inputs: &["test_exercises.py"],
            },
            Self::Rust => Workspace {
                directory: "practice/rust",
                starter: "starter.rs",
                answers: "answers.rs",
                inputs: &["Cargo.toml", "Cargo.lock", "checks.rs", "target"],
            },
        }
    }
}

impl fmt::Display for Language {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(match self {
            Self::Python => "python",
            Self::Rust => "rust",
        })
    }
}

pub struct Workspace {
    pub directory: &'static str,
    pub starter: &'static str,
    pub answers: &'static str,
    pub inputs: &'static [&'static str],
}

#[derive(Clone, Copy)]
pub enum NativeCheck {
    Python(&'static str),
    Rust(&'static str),
}

pub struct Exercise {
    pub id: &'static str,
    pub language: Language,
    pub title: &'static str,
    pub prompt: &'static str,
    pub hint: &'static str,
    pub check: NativeCheck,
}

pub const CATALOG: &[Exercise] = &[
    Exercise {
        id: "python/hello",
        language: Language::Python,
        title: "Hello, World!",
        prompt: "Implement hello() -> None. Print exactly Hello, World! followed by a newline, and return None.",
        hint: "Consider how Python's console output function ends a line and what a function returns when no value is specified.",
        check: NativeCheck::Python("test_exercises.PracticeTests.test_hello"),
    },
    Exercise {
        id: "python/find_in_string",
        language: Language::Python,
        title: "Find in String",
        prompt: "Implement find_in_string(string: str, substring: str) -> int. Return the zero-based index of the first occurrence, or -1 if absent. An empty substring matches at 0, even in an empty string. Matching is case-sensitive; built-in string operations are allowed.",
        hint: "Look for a string search operation that reports a missing match without raising an exception. Consider the empty-substring case.",
        check: NativeCheck::Python("test_exercises.PracticeTests.test_find_in_string"),
    },
    Exercise {
        id: "python/length_of_last_word",
        language: Language::Python,
        title: "Length of Last Word",
        prompt: "Implement length_of_last_word(text: str) -> int. Return the length of the final whitespace-separated word, ignoring leading and trailing whitespace. Spaces, tabs, and newlines separate words. Empty or whitespace-only input returns 0. Punctuation remains part of a word.",
        hint: "Consider splitting on general whitespace rather than literal spaces, and handle the case where there are no words before accessing the last one.",
        check: NativeCheck::Python("test_exercises.PracticeTests.test_length_of_last_word"),
    },
    Exercise {
        id: "rust/hello",
        language: Language::Rust,
        title: "Hello, World!",
        prompt: "Implement pub fn greeting() -> &'static str. Return exactly Hello, World!; printing the message is not sufficient.",
        hint: "A string literal has a static lifetime. Consider the difference between returning a value and printing it.",
        check: NativeCheck::Rust("hello"),
    },
];

#[derive(Debug, PartialEq, Eq)]
pub enum Outcome {
    Passed,
    AttemptFailed,
    Blocked(String),
    Indeterminate(String),
}

impl Outcome {
    pub fn code(&self) -> u8 {
        match self {
            Self::Passed => 0,
            Self::AttemptFailed => 1,
            Self::Blocked(_) => 2,
            Self::Indeterminate(_) => 3,
        }
    }
}

impl fmt::Display for Outcome {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Passed => f.write_str("Passed"),
            Self::AttemptFailed => f.write_str("Attempt failed"),
            Self::Blocked(reason) => write!(f, "Blocked: {reason}"),
            Self::Indeterminate(reason) => write!(f, "Indeterminate: {reason}"),
        }
    }
}
