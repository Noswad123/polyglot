use std::fmt;

pub use crate::library::{
    Problem, QuestionStatus, BINARY_SEARCH, FIBONACCI, FIND_IN_STRING, HELLO_WORLD,
    LENGTH_OF_LAST_WORD, PROBLEMS,
};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Language {
    Python,
    Rust,
    TypeScript,
    Go,
    Bash,
    Lua,
}

impl Language {
    pub const ALL: [Self; 6] = [
        Self::Python,
        Self::Rust,
        Self::TypeScript,
        Self::Go,
        Self::Bash,
        Self::Lua,
    ];

    pub fn names() -> String {
        Self::ALL
            .iter()
            .map(ToString::to_string)
            .collect::<Vec<_>>()
            .join("|")
    }

    pub fn parse(value: &str) -> Option<Self> {
        match value {
            "python" => Some(Self::Python),
            "rust" => Some(Self::Rust),
            "typescript" => Some(Self::TypeScript),
            "go" => Some(Self::Go),
            "bash" => Some(Self::Bash),
            "lua" => Some(Self::Lua),
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
                inputs: &["Cargo.toml", "Cargo.lock", "target"],
            },
            Self::TypeScript => Workspace {
                directory: "practice/typescript",
                inputs: &["package.json"],
            },
            Self::Go => Workspace {
                directory: "practice/go",
                inputs: &[],
            },
            Self::Bash => Workspace {
                directory: "practice/bash",
                inputs: &[],
            },
            Self::Lua => Workspace {
                directory: "practice/lua",
                inputs: &[],
            },
        }
    }
}

impl fmt::Display for Language {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(match self {
            Self::Python => "python",
            Self::Rust => "rust",
            Self::TypeScript => "typescript",
            Self::Go => "go",
            Self::Bash => "bash",
            Self::Lua => "lua",
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
    Rust(RustCheck),
    TypeScript {
        harness: &'static str,
        config: &'static str,
        api: &'static str,
    },
    Go {
        harness: &'static str,
    },
    Bash {
        harness: &'static str,
    },
    Lua {
        harness: &'static str,
    },
}

#[derive(Clone, Copy)]
pub struct RustCheck {
    pub target: &'static str,
    pub selector: &'static str,
    pub harness: &'static str,
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
        check: NativeCheck::Rust(RustCheck {
            target: "practice_checks",
            selector: "hello",
            harness: "checks.rs",
        }),
    },
    Exercise {
        id: "rust/find_in_string",
        file: "exercises/find_in_string.rs",
        language: Language::Rust,
        problem: &FIND_IN_STRING,
        prompt: "Implement pub fn find_in_string(string: &str, substring: &str) -> isize. For ASCII inputs, return the first match index or -1; an empty substring matches at 0.",
        hint: "Rust's str::find returns an Option<usize>. Convert the first match index to isize, or return -1 when absent.",
        check: NativeCheck::Rust(RustCheck {
            target: "find_in_string_checks",
            selector: "find_in_string",
            harness: "tests/find_in_string.rs",
        }),
    },
    Exercise {
        id: "rust/length_of_last_word",
        file: "exercises/length_of_last_word.rs",
        language: Language::Rust,
        problem: &LENGTH_OF_LAST_WORD,
        prompt: "Implement pub fn length_of_last_word(text: &str) -> usize for the shared ASCII input scope; return the last word's length, or 0 when no words exist.",
        hint: "Consider split_whitespace and a double-ended iterator to find the last word, then handle the no-words case.",
        check: NativeCheck::Rust(RustCheck {
            target: "length_of_last_word_checks",
            selector: "length_of_last_word",
            harness: "tests/length_of_last_word.rs",
        }),
    },
    Exercise {
        id: "rust/binary_search",
        file: "exercises/binary_search.rs",
        language: Language::Rust,
        problem: &BINARY_SEARCH,
        prompt: "Implement pub fn binary_search(target: i32, arr: &[i32]) -> bool. Return whether target occurs in the sorted slice without mutating it; halve the search interval.",
        hint: "Keep a half-open interval of usize indices and compare its midpoint with target. Setting the upper bound to mid avoids subtracting from zero.",
        check: NativeCheck::Rust(RustCheck {
            target: "binary_search_checks",
            selector: "binary_search",
            harness: "tests/binary_search.rs",
        }),
    },
    Exercise {
        id: "rust/fibonacci",
        file: "exercises/fibonacci.rs",
        language: Language::Rust,
        problem: &FIBONACCI,
        prompt: "Implement pub fn fibonacci(length: usize) -> Vec<u32>. For length in 0..=40, return exactly length terms starting 1, 1; length 0 returns an empty vector.",
        hint: "Build a Vec<u32> from the two most recent terms, handling lengths 0 and 1 without adding extra terms.",
        check: NativeCheck::Rust(RustCheck {
            target: "fibonacci_checks",
            selector: "fibonacci",
            harness: "tests/fibonacci.rs",
        }),
    },
    Exercise {
        id: "typescript/hello", file: "exercises/hello.ts", language: Language::TypeScript,
        problem: &HELLO_WORLD,
        prompt: "Export function hello(): void. Print exactly Hello, World! followed by one newline and return undefined.",
        hint: "Consider the difference between returning text and writing a line to the console.",
        check: NativeCheck::TypeScript { harness: "tests/check_hello.cjs", config: "tests/hello.tsconfig.json", api: "tests/hello_api.ts" },
    },
    Exercise {
        id: "go/hello", file: "exercises/hello.go", language: Language::Go,
        problem: &HELLO_WORLD,
        prompt: "In package exercises, implement func Hello() string returning exactly Hello, World! without a newline. Printing is not a substitute.",
        hint: "A string literal can be returned directly; the caller decides how to display it.",
        check: NativeCheck::Go { harness: "tests/hello_test.go" },
    },
    Exercise {
        id: "bash/hello", file: "exercises/hello.sh", language: Language::Bash,
        problem: &HELLO_WORLD,
        prompt: "Define the hello shell function. When called, print exactly Hello, World! and one newline, with status 0. Do not run a top-level demo.",
        hint: "Consider printf and the exit status of the function's final command.",
        check: NativeCheck::Bash { harness: "tests/check_hello.sh" },
    },
    Exercise {
        id: "lua/hello", file: "exercises/hello.lua", language: Language::Lua,
        problem: &HELLO_WORLD,
        prompt: "Define global function hello(). When called, print exactly Hello, World! and one newline; return no values or a single nil. Do not run a top-level demo.",
        hint: "Consider how print terminates a line and what happens without a return statement.",
        check: NativeCheck::Lua { harness: "tests/check_hello.lua" },
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
    fn curated_batch_has_both_languages_and_independent_rust_targets() {
        for problem in [
            &HELLO_WORLD,
            &FIND_IN_STRING,
            &LENGTH_OF_LAST_WORD,
            &BINARY_SEARCH,
            &FIBONACCI,
        ] {
            let bindings: Vec<_> = CATALOG
                .iter()
                .filter(|exercise| std::ptr::eq(exercise.problem, problem))
                .collect();
            assert_eq!(
                bindings
                    .iter()
                    .filter(|e| matches!(e.language, Language::Python | Language::Rust))
                    .count(),
                2
            );
            assert_eq!(
                bindings.len(),
                if problem.id == HELLO_WORLD.id { 6 } else { 2 }
            );
            assert!(bindings
                .iter()
                .any(|exercise| exercise.language == Language::Python));
            assert!(bindings
                .iter()
                .any(|exercise| exercise.language == Language::Rust));
        }
        let mut targets = HashSet::new();
        let mut harnesses = HashSet::new();
        for exercise in CATALOG {
            if let NativeCheck::Rust(check) = exercise.check {
                assert!(targets.insert(check.target));
                assert!(harnesses.insert(check.harness));
                assert!(check
                    .target
                    .bytes()
                    .all(|byte| byte.is_ascii_alphanumeric() || byte == b'_'));
                assert_eq!(exercise.id.rsplit('/').next(), Some(check.selector));
                assert!(Path::new(check.harness)
                    .components()
                    .all(|part| matches!(part, Component::Normal(_))));
            }
        }
        assert_eq!(targets.len(), 5);
    }

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
        assert_eq!(references.len(), 74);
        assert_eq!(statuses, [5, 15, 17]);
        for (language, count) in [
            ("python", 26),
            ("typescript", 28),
            ("javascript", 3),
            ("go", 4),
            ("rust", 6),
            ("bash", 3),
            ("lua", 3),
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
        assert_eq!(exercises.len(), 14);
    }
}
