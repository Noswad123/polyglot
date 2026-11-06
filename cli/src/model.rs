use std::fmt;

pub use crate::library::{
    Problem, QuestionStatus, BINARY_SEARCH, FIBONACCI, FIND_IN_STRING, HELLO_WORLD,
    LENGTH_OF_LAST_WORD, PROBLEMS,
};

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
                inputs: &[
                    "exercises/__init__.py",
                    "tests/__init__.py",
                    "tests/feedback.py",
                ],
            },
            Self::Rust => Workspace {
                directory: "practice/rust",
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
    pub inputs: &'static [&'static str],
}

#[derive(Clone, Copy)]
pub enum NativeCheck {
    Python(&'static str),
    Rust(&'static str),
}

pub struct Exercise {
    pub id: &'static str,
    pub file: &'static str,
    pub language: Language,
    pub problem: &'static Problem,
    pub prompt: &'static str,
    pub hint: &'static str,
    pub check: NativeCheck,
}

pub const CATALOG: &[Exercise] = &[
    Exercise {
        id: "python/hello",
        file: "exercises/hello.py",
        language: Language::Python,
        problem: &HELLO_WORLD,
        prompt: "Implement hello() -> None using the Python binding in the shared question.",
        hint: "Consider how Python's console output function ends a line and what a function returns when no value is specified.",
        check: NativeCheck::Python("tests.test_hello.PracticeTests.test_hello"),
    },
    Exercise {
        id: "python/find_in_string",
        file: "exercises/find_in_string.py",
        language: Language::Python,
        problem: &FIND_IN_STRING,
        prompt: "Implement find_in_string(string: str, substring: str) -> int.",
        hint: "Look for a string search operation that reports a missing match without raising an exception. Consider the empty-substring case.",
        check: NativeCheck::Python("tests.test_find_in_string.PracticeTests.test_find_in_string"),
    },
    Exercise {
        id: "python/length_of_last_word",
        file: "exercises/length_of_last_word.py",
        language: Language::Python,
        problem: &LENGTH_OF_LAST_WORD,
        prompt: "Implement length_of_last_word(text: str) -> int.",
        hint: "Consider splitting on general whitespace rather than literal spaces, and handle the case where there are no words before accessing the last one.",
        check: NativeCheck::Python("tests.test_length_of_last_word.PracticeTests.test_length_of_last_word"),
    },
    Exercise {
        id: "python/binary_search",
        file: "exercises/binary_search.py",
        language: Language::Python,
        problem: &BINARY_SEARCH,
        prompt: "Implement binary_search(target: int, arr: list[int]) -> bool.",
        hint: "Track the remaining search interval and compare its middle value with the target. Be careful when shrinking the interval at its boundaries.",
        check: NativeCheck::Python("tests.test_binary_search.PracticeTests.test_binary_search"),
    },
    Exercise {
        id: "python/fibonacci",
        file: "exercises/fibonacci.py",
        language: Language::Python,
        problem: &FIBONACCI,
        prompt: "Implement fibonacci(length: int) -> list[int].",
        hint: "Handle the shortest requested lengths first, then use the two most recent terms to extend the list.",
        check: NativeCheck::Python("tests.test_fibonacci.PracticeTests.test_fibonacci"),
    },
    Exercise {
        id: "rust/hello",
        file: "exercises/hello.rs",
        language: Language::Rust,
        problem: &HELLO_WORLD,
        prompt: "Implement pub fn greeting() -> &'static str using the Rust binding in the shared question.",
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

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashSet;
    use std::path::{Component, Path};

    #[test]
    fn catalog_has_unique_ids_and_registered_safe_questions() {
        let mut problems = HashSet::new();
        let mut documents = HashSet::new();
        let mut references = HashSet::new();
        let mut languages = std::collections::HashMap::new();
        let mut statuses = [0; 3];
        for problem in PROBLEMS {
            assert!(problems.insert(problem.id));
            assert!(!problem.id.is_empty());
            assert!(problem
                .id
                .bytes()
                .all(|byte| byte.is_ascii_lowercase() || byte == b'-'));
            statuses[match problem.question_status {
                QuestionStatus::Curated => 0,
                QuestionStatus::Draft => 1,
                QuestionStatus::Missing => 2,
            }] += 1;
            assert_eq!(
                problem.question_doc.is_none(),
                problem.question_status == QuestionStatus::Missing
            );
            if let Some(document) = problem.question_doc {
                assert!(documents.insert(document));
                let path = Path::new(document);
                assert!(path.starts_with("README/katas"));
                assert!(path
                    .components()
                    .all(|part| matches!(part, Component::Normal(_))));
                assert_eq!(path.extension().unwrap(), "md");
            }
            for reference in problem.references {
                assert!(references.insert(reference.path));
                let root = match reference.language {
                    "python" => "practice/python/soutions",
                    "typescript" => "practice/typescript",
                    "javascript" => "practice/javascript",
                    "go" => "practice/go",
                    "rust" => "practice/rust/solutions",
                    "bash" => "practice/bash",
                    "lua" => "practice/lua",
                    "lisp" => "practice/lisp",
                    language => panic!("Unknown implementation language: {language}"),
                };
                *languages.entry(reference.language).or_insert(0) += 1;
                let path = Path::new(reference.path);
                let relative = path
                    .strip_prefix(root)
                    .expect("Implementation root mismatch");
                assert!(!relative.as_os_str().is_empty());
                assert!(!relative.components().any(|part| matches!(
                    part.as_os_str().to_str(),
                    Some("exercises" | "tests" | "compat" | "target" | "build")
                )));
                assert!(path
                    .components()
                    .all(|part| matches!(part, Component::Normal(_))));
            }
        }
        assert_eq!(problems.len(), 37);
        assert_eq!(documents.len(), 20);
        assert_eq!(references.len(), 60);
        assert_eq!(statuses, [5, 15, 17]);
        for (language, count) in [
            ("python", 21),
            ("typescript", 27),
            ("javascript", 3),
            ("go", 3),
            ("rust", 1),
            ("bash", 2),
            ("lua", 2),
            ("lisp", 1),
        ] {
            assert_eq!(languages[language], count);
        }
        assert!(PROBLEMS.windows(2).all(|pair| pair[0].id < pair[1].id));
        let mut exercises = HashSet::new();
        for exercise in CATALOG {
            assert!(exercises.insert(exercise.id));
            assert!(exercise.id.starts_with(&format!("{}/", exercise.language)));
            assert_eq!(exercise.problem.question_status, QuestionStatus::Curated);
            assert!(exercise.problem.question_doc.is_some());
            assert!(PROBLEMS
                .iter()
                .any(|problem| std::ptr::eq(*problem, exercise.problem)));
        }
        assert_eq!(exercises.len(), 6);
    }
}
