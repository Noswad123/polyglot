use std::fs;
use std::io::{self, Write};
use std::path::Path;
use std::process::Command;

use serde_json::Value;

use super::support::Scratch;
use super::{diagnostics, output, tool, Tools};
use crate::model::{Exercise, NativeCheck, Outcome};

pub fn check(
    _root: &Path,
    directory: &Path,
    exercises: &[&Exercise],
    tools: &Tools,
) -> Result<Outcome, Outcome> {
    let executable = tool(tools.go.as_deref().unwrap_or(Path::new("go")))?;
    let command = || {
        let mut command = Command::new(&executable);
        command
            .env("GO111MODULE", "off")
            .env("GOWORK", "off")
            .env("GOPROXY", "off")
            .env("GOSUMDB", "off")
            .env("GOTOOLCHAIN", "local")
            .env("GOENV", "off")
            .env_remove("GOFLAGS");
        command
    };
    let version = output(command().arg("version"))?;
    diagnostics(&version);
    let version_text = String::from_utf8_lossy(&version.stdout);
    let minor = version_text
        .split_whitespace()
        .find_map(|part| part.strip_prefix("go1."))
        .and_then(|part| part.split('.').next()?.parse::<u32>().ok());
    if !version.status.success() || minor.is_none_or(|minor| minor < 20) {
        return Err(Outcome::Blocked(
            "Go >=1.20 is required (automatic toolchain downloads are disabled)".into(),
        ));
    }
    for exercise in exercises {
        let NativeCheck::Go { harness } = exercise.check else {
            return Err(Outcome::Blocked("invalid Go selector".into()));
        };
        let scratch = Scratch::new("go")?;
        for (from, name) in [
            (directory.join(exercise.file), "hello.go"),
            (directory.join(harness), "hello_test.go"),
        ] {
            fs::copy(&from, scratch.path.join(name))
                .map_err(|error| Outcome::Blocked(format!("copy {}: {error}", from.display())))?;
        }
        let harness_text = fs::read_to_string(scratch.path.join("hello_test.go"))
            .map_err(|error| Outcome::Blocked(error.to_string()))?;
        let api_lines: Vec<_> = harness_text
            .lines()
            .enumerate()
            .filter(|(_, line)| {
                line.split_once("// polyglot:api")
                    .and_then(|(code, _)| code.split_once('='))
                    .is_some_and(|(_, expression)| expression.trim() == "Hello")
            })
            .map(|(index, _)| index + 1)
            .collect();
        println!(
            "Checking {} (isolated copy: {})",
            directory.join(exercise.file).display(),
            scratch.path.join("hello.go").display()
        );
        let result = output(command().current_dir(&scratch.path).args([
            "test",
            "-json",
            "-count=1",
            "-run",
            "^TestHello$",
            "hello.go",
            "hello_test.go",
        ]))?;
        let _ = io::stderr().write_all(&result.stderr);
        let mut native = String::from_utf8_lossy(&result.stderr).into_owned();
        let mut ran = false;
        let mut passed = false;
        let mut failed = false;
        let mut skipped = false;
        let mut package_passed = false;
        let mut malformed = false;
        for line in result
            .stdout
            .split(|byte| *byte == b'\n')
            .filter(|line| !line.is_empty())
        {
            let Ok(message) = serde_json::from_slice::<Value>(line) else {
                let text = String::from_utf8_lossy(line);
                println!("{text}");
                native.push_str(&text);
                native.push('\n');
                malformed = true;
                continue;
            };
            if let Some(text) = message["Output"].as_str() {
                print!("{text}");
                native.push_str(text);
            }
            if message["Test"] == "TestHello" {
                match message["Action"].as_str() {
                    Some("run") => ran = true,
                    Some("pass") => passed = true,
                    Some("fail") => failed = true,
                    Some("skip") => skipped = true,
                    _ => {}
                }
            } else if message["Test"].is_null() && message["Action"] == "pass" {
                package_passed = true;
            }
        }
        let mut source_error = false;
        let mut harness_error = false;
        // Test assertion locations look like compiler locations; attribute only
        // diagnostics emitted before the selected test could run.
        for line in native.lines().filter(|_| !ran) {
            let line = line.trim();
            let (name, location) = line.split_once(':').unwrap_or(("", ""));
            let filename = Path::new(name).file_name().and_then(|name| name.to_str());
            if filename == Some("hello.go") {
                source_error = true;
            } else if filename == Some("hello_test.go") {
                let api_error = location
                    .split(':')
                    .next()
                    .and_then(|number| number.parse::<usize>().ok())
                    .is_some_and(|number| api_lines.contains(&number))
                    && (line.contains("undefined: Hello")
                        || line.contains("cannot use Hello")
                        || line.contains("Hello (value of type")
                        || line.contains("Hello (type) is not an expression")
                        || line
                            .contains("cannot use generic function Hello without instantiation")
                        || (line.contains("cannot infer ")
                            && line.contains("(declared at ")
                            && line.contains("hello.go:")));
                if api_error {
                    source_error = true;
                } else {
                    harness_error = true;
                }
            } else if line.contains("found packages") && line.contains("hello.go") {
                if line.contains("exercises (hello_test.go)") {
                    source_error = true;
                } else {
                    harness_error = true;
                }
            }
        }
        if harness_error {
            return Ok(Outcome::Blocked(
                "selected Go test harness did not compile".into(),
            ));
        }
        if source_error {
            return Ok(Outcome::AttemptFailed);
        }
        if skipped {
            return Ok(Outcome::Blocked(
                "TestHello was skipped, not checked".into(),
            ));
        }
        if ran && passed && package_passed && result.status.success() && !malformed {
            continue;
        }
        if ran && failed && !result.status.success() {
            return Ok(Outcome::AttemptFailed);
        }
        if !ran && package_passed && result.status.success() && native.contains("no tests to run") {
            return Ok(Outcome::Blocked(
                "intended Go test TestHello was not selected (zero or renamed tests)".into(),
            ));
        }
        return Ok(Outcome::Indeterminate(format!(
            "Go did not report a normal TestHello completion ({})",
            result.status
        )));
    }
    Ok(Outcome::Passed)
}
