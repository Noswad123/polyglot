use std::fs;
use std::io::{self, Write};
use std::path::{Component, Path, PathBuf};
use std::process::Command;

use serde_json::Value;

use super::{diagnostics, output, tool};
use crate::model::{Exercise, NativeCheck, Outcome};
use crate::workspace::safe_path;

fn normalized(path: &Path) -> PathBuf {
    let mut result = PathBuf::new();
    for component in path.components() {
        match component {
            Component::CurDir => {}
            Component::ParentDir => {
                result.pop();
            }
            other => result.push(other.as_os_str()),
        }
    }
    result
}

fn span_matches(span: &Value, directory: &Path, source: &Path) -> bool {
    span["file_name"].as_str().is_some_and(|name| {
        let path = Path::new(name);
        let path = if path.is_absolute() {
            path.to_path_buf()
        } else {
            directory.join(path)
        };
        normalized(&path) == normalized(source)
    })
}

fn primary_span(diagnostic: &Value, directory: &Path, source: &Path) -> bool {
    diagnostic["spans"].as_array().is_some_and(|spans| {
        spans
            .iter()
            .any(|span| span["is_primary"] == true && span_matches(span, directory, source))
    })
}

// The trusted harness marks its typed API assignment. Signature/name/visibility
// mistakes there are learner interface errors, not broken test configuration.
fn api_contract_error(diagnostic: &Value, directory: &Path, harness: &Path) -> bool {
    if !matches!(
        diagnostic["code"]["code"].as_str(),
        Some("E0308" | "E0425" | "E0603")
    ) {
        return false;
    }
    diagnostic["spans"].as_array().is_some_and(|spans| {
        spans.iter().any(|span| {
            span["is_primary"] == true
                && span_matches(span, directory, harness)
                && span["text"].as_array().is_some_and(|lines| {
                    lines.iter().any(|line| {
                        line["text"]
                            .as_str()
                            .is_some_and(|text| text.contains("// polyglot:api"))
                    })
                })
        })
    })
}

fn validate_target(target: &Path) -> Result<(), Outcome> {
    let mut pending = vec![target.to_path_buf()];
    while let Some(path) = pending.pop() {
        let metadata = match fs::symlink_metadata(&path) {
            Ok(metadata) => metadata,
            Err(error) if error.kind() == io::ErrorKind::NotFound && path == target => continue,
            Err(error) => return Err(Outcome::Blocked(format!("{}: {error}", path.display()))),
        };
        if metadata.file_type().is_symlink() {
            return Err(Outcome::Blocked(format!(
                "symlink is not allowed: {}",
                path.display()
            )));
        }
        if metadata.is_dir() {
            let entries = fs::read_dir(&path)
                .map_err(|error| Outcome::Blocked(format!("{}: {error}", path.display())))?;
            for entry in entries {
                let entry = entry
                    .map_err(|error| Outcome::Blocked(format!("{}: {error}", path.display())))?;
                pending.push(entry.path());
            }
        } else if path == target || !metadata.is_file() {
            return Err(Outcome::Blocked(format!(
                "expected a target directory containing only regular files and directories: {}",
                path.display()
            )));
        }
    }
    Ok(())
}

pub fn check(
    root: &Path,
    directory: &Path,
    exercises: &[&Exercise],
    override_path: Option<&Path>,
) -> Result<Outcome, Outcome> {
    for exercise in exercises {
        let outcome = check_one(root, directory, exercise, override_path)?;
        if outcome != Outcome::Passed {
            return Ok(outcome);
        }
    }
    Ok(Outcome::Passed)
}

fn check_one(
    root: &Path,
    directory: &Path,
    exercise: &Exercise,
    override_path: Option<&Path>,
) -> Result<Outcome, Outcome> {
    let NativeCheck::Rust(check) = exercise.check else {
        return Err(Outcome::Blocked("invalid Rust selector".into()));
    };
    let target = directory.join("target");
    // Validate before Cargo can write through an existing nested symlink.
    validate_target(&target)?;
    let cargo = tool(override_path.unwrap_or(Path::new("cargo")))?;
    let version = output(Command::new(&cargo).arg("--version"))?;
    diagnostics(&version);
    if !version.status.success() {
        return Err(Outcome::Blocked(format!(
            "Cargo version probe failed ({})",
            version.status
        )));
    }
    println!("Cargo: {}", cargo.display());
    let result = output(
        Command::new(&cargo)
            .current_dir(directory)
            .args(["test", "--offline", "--locked", "--manifest-path"])
            .arg(directory.join("Cargo.toml"))
            .args([
                "--test",
                check.target,
                "--no-run",
                "--message-format=json",
                "--target-dir",
            ])
            .arg(&target),
    )?;
    let _ = io::stderr().write_all(&result.stderr);
    let mut executable = None;
    let mut answer_errors = false;
    let mut harness_errors = false;
    let mut unknown_errors = false;
    let mut finished = false;
    let mut malformed = false;
    for line in result
        .stdout
        .split(|byte| *byte == b'\n')
        .filter(|line| !line.is_empty())
    {
        let Ok(message) = serde_json::from_slice::<Value>(line) else {
            let _ = io::stdout().write_all(line);
            let _ = io::stdout().write_all(b"\n");
            malformed = true;
            continue;
        };
        match message["reason"].as_str() {
            Some("compiler-message") => {
                let diagnostic = &message["message"];
                if let Some(rendered) = diagnostic["rendered"].as_str() {
                    eprint!("{rendered}");
                }
                if diagnostic["level"] == "error" {
                    if primary_span(diagnostic, directory, &directory.join(exercise.file))
                        || api_contract_error(diagnostic, directory, &directory.join(check.harness))
                    {
                        answer_errors = true;
                    } else if primary_span(diagnostic, directory, &directory.join(check.harness))
                        || diagnostic["code"]["code"] == "E0463"
                        || diagnostic["message"].as_str().is_some_and(|message| {
                            message.starts_with(&format!("couldn't read `{}`", check.harness))
                        })
                    {
                        harness_errors = true;
                    } else {
                        unknown_errors = true;
                    }
                }
            }
            Some("compiler-artifact")
                if message["target"]["name"] == check.target
                    && message["profile"]["test"] == true =>
            {
                if let Some(path) = message["executable"].as_str() {
                    executable = Some(PathBuf::from(path));
                }
            }
            Some("build-finished") => finished = message["success"] == true,
            _ => {}
        }
    }
    if malformed {
        return Err(Outcome::Indeterminate("unrecognized Cargo output".into()));
    }
    if !result.status.success() {
        if unknown_errors {
            return Ok(Outcome::Indeterminate(format!(
                "compiler errors could not be attributed to answers or the harness ({})",
                result.status
            )));
        }
        if harness_errors {
            return Ok(Outcome::Blocked(
                "Rust check harness did not compile".into(),
            ));
        }
        if answer_errors {
            return Ok(Outcome::AttemptFailed);
        }
        let stderr = String::from_utf8_lossy(&result.stderr);
        if [
            "failed to parse manifest",
            "failed to parse lock file",
            "--locked was passed",
            "could not load Cargo configuration",
            "Cargo.toml:",
            "no test target named",
            "manifest path",
            "could not find",
            "failed to load",
            "no matching package",
            "failed to download",
            "requires rustc",
            "can't find",
            "could not execute process",
            "does not support",
            "is not installed",
        ]
        .iter()
        .any(|message| stderr.contains(message))
        {
            return Ok(Outcome::Blocked(format!(
                "Cargo configuration/toolchain prevented checking ({})",
                result.status
            )));
        }
        return Ok(Outcome::Indeterminate(format!(
            "Cargo failed without attributable compiler diagnostics ({})",
            result.status
        )));
    }
    if !finished || answer_errors || harness_errors || unknown_errors {
        return Err(Outcome::Indeterminate(
            "Cargo did not confirm a successful build".into(),
        ));
    }
    let executable = executable
        .ok_or_else(|| Outcome::Blocked("Cargo produced no practice test executable".into()))?;
    let relative = executable
        .strip_prefix(root)
        .map_err(|_| Outcome::Blocked("Cargo test executable is outside the checkout".into()))?;
    let executable = safe_path(root, relative)?;
    if !executable.starts_with(&target) {
        return Err(Outcome::Blocked(
            "Cargo test executable is outside the isolated target directory".into(),
        ));
    }
    let selector = check.selector;
    let inventory = output(
        Command::new(&executable)
            .current_dir(directory)
            .args(["--list", "--format", "terse", "--exact", selector]),
    )?;
    diagnostics(&inventory);
    if !inventory.status.success() {
        return Err(Outcome::Indeterminate(format!(
            "Rust test inventory failed ({})",
            inventory.status
        )));
    }
    if String::from_utf8_lossy(&inventory.stdout).trim() != format!("{selector}: test") {
        return Err(Outcome::Blocked(
            "intended Rust test was not selected (zero or unexpected tests)".into(),
        ));
    }
    let result = output(Command::new(&executable).current_dir(directory).args([
        selector,
        "--exact",
        "--nocapture",
        "--test-threads=1",
    ]))?;
    diagnostics(&result);
    let stdout = String::from_utf8_lossy(&result.stdout);
    if result.status.success()
        && stdout
            .lines()
            .any(|line| line.starts_with("test result: ok. 1 passed; 0 failed; 0 ignored;"))
    {
        return Ok(Outcome::Passed);
    }
    if result.status.code() == Some(101)
        && stdout
            .lines()
            .any(|line| line.starts_with("test result: FAILED. 0 passed; 1 failed; 0 ignored;"))
    {
        return Ok(Outcome::AttemptFailed);
    }
    Ok(Outcome::Indeterminate(format!(
        "Rust test did not report a normal single-test result ({})",
        result.status
    )))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn api_errors_require_a_marked_primary_harness_assignment() {
        let directory = Path::new("/checkout/practice/rust");
        let harness = directory.join("tests/find_in_string.rs");
        let mut diagnostic = serde_json::json!({
            "code": {"code": "E0308"},
            "spans": [{"is_primary": true, "file_name": "tests/find_in_string.rs",
                "text": [{"text": "const FUNCTION: fn(&str, &str) -> isize = exercise::find_in_string; // polyglot:api"}]}]
        });
        assert!(api_contract_error(&diagnostic, directory, &harness));
        assert!(!api_contract_error(
            &diagnostic,
            directory,
            &directory.join("checks.rs")
        ));
        diagnostic["spans"][0]["text"][0]["text"] = "let value: usize = false;".into();
        assert!(!api_contract_error(&diagnostic, directory, &harness));
        diagnostic["spans"][0]["text"][0]["text"] = "// polyglot:api".into();
        diagnostic["code"]["code"] = "E0061".into();
        assert!(!api_contract_error(&diagnostic, directory, &harness));
    }

    #[test]
    fn compiler_errors_require_a_primary_answer_span() {
        let directory = Path::new("/checkout/practice/rust");
        let answer = &directory.join("exercises/hello.rs");
        assert!(primary_span(
            &serde_json::json!({"spans": [{"file_name": "exercises/hello.rs", "is_primary": true}]}),
            directory,
            answer
        ));
        assert!(primary_span(
            &serde_json::json!({"spans": [{"file_name": "tests/../exercises/hello.rs", "is_primary": true}]}),
            directory,
            answer
        ));
        assert!(!primary_span(
            &serde_json::json!({"spans": [{"file_name": "checks.rs", "is_primary": true}, {"file_name": "exercises/hello.rs", "is_primary": false}]}),
            directory,
            answer
        ));
        assert!(!primary_span(
            &serde_json::json!({"spans": []}),
            directory,
            answer
        ));
        assert!(!primary_span(
            &serde_json::json!({"spans": [{"file_name": "/other/answers.rs", "is_primary": true}]}),
            directory,
            answer
        ));
    }
}
