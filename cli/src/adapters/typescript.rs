use std::fs;
use std::path::Path;
use std::process::{Command, Stdio};

use serde_json::Value;

use super::support::Scratch;
use super::{diagnostics, output, tool, Tools};
use crate::model::{Exercise, NativeCheck, Outcome};

const SETUP: &str = "Install Node >=18 and run npm ci --prefix practice/typescript; use --node PATH and --tsc PATH before the command to select tools. --tsc must point to the actual npm typescript/bin/tsc entry, not a Volta or other executable shim.";

pub fn check(
    root: &Path,
    directory: &Path,
    exercises: &[&Exercise],
    tools: &Tools,
) -> Result<Outcome, Outcome> {
    let node = tool(tools.node.as_deref().unwrap_or(Path::new("node")))
        .map_err(|error| Outcome::Blocked(format!("{error}. {SETUP}")))?;
    let version = output(Command::new(&node).arg("--version"))?;
    let node_version = String::from_utf8_lossy(&version.stdout);
    let major = node_version
        .trim()
        .strip_prefix('v')
        .and_then(|version| version.split('.').next())
        .and_then(|major| major.parse::<u64>().ok());
    if !version.status.success() || major.is_none_or(|major| major < 18) {
        diagnostics(&version);
        return Err(Outcome::Blocked(format!("Node >=18 is required. {SETUP}")));
    }
    let local = root.join("practice/typescript/node_modules/typescript/bin/tsc");
    let selected = tools.tsc.as_deref().unwrap_or_else(|| {
        if fs::symlink_metadata(&local).is_ok() {
            &local
        } else {
            Path::new("tsc")
        }
    });
    let entry = tool(selected)
        .and_then(|entry| {
            fs::canonicalize(&entry).map_err(|error| {
                Outcome::Blocked(format!("cannot resolve {}: {error}", entry.display()))
            })
        })
        .map_err(|error| Outcome::Blocked(format!("{error}. {SETUP}")))?;
    let package = entry
        .parent()
        .and_then(Path::parent)
        .ok_or_else(|| Outcome::Blocked(format!("invalid TypeScript compiler entry. {SETUP}")))?;
    let compiler = package.join("lib/typescript.js");
    let package_info: Value = fs::read(package.join("package.json"))
        .ok()
        .and_then(|bytes| serde_json::from_slice(&bytes).ok())
        .unwrap_or(Value::Null);
    if entry.file_name().is_none_or(|name| name != "tsc")
        || entry
            .parent()
            .and_then(Path::file_name)
            .is_none_or(|name| name != "bin")
        || package_info["name"] != "typescript"
        || !compiler.is_file()
    {
        return Err(Outcome::Blocked(format!(
            "{} is not an actual npm TypeScript bin/tsc entry. {SETUP}",
            entry.display()
        )));
    }
    let version = output(Command::new(&node).arg(&entry).arg("--version"))?;
    if !version.status.success() {
        diagnostics(&version);
        return Err(Outcome::Blocked(format!(
            "TypeScript version probe failed. {SETUP}"
        )));
    }
    let api = output(
        Command::new(&node)
            .args(["-e", "const ts = require(process.argv[1]); console.log(JSON.stringify({version: ts.version, api: typeof ts.createProgram === 'function'}));"])
            .arg(&compiler),
    )?;
    let info: Value = serde_json::from_slice(&api.stdout).unwrap_or(Value::Null);
    let compiler_version = info["version"].as_str().unwrap_or("");
    let major = compiler_version
        .split('.')
        .next()
        .and_then(|value| value.parse::<u64>().ok());
    if !api.status.success()
        || info["api"] != true
        || major.is_none_or(|major| major < 5)
        || String::from_utf8_lossy(&version.stdout).trim() != format!("Version {compiler_version}")
    {
        diagnostics(&api);
        return Err(Outcome::Blocked(format!(
            "TypeScript >=5 with a working compiler API is required. {SETUP}"
        )));
    }
    println!("Node: {} ({})", node.display(), node_version.trim());
    println!("TypeScript: {} ({compiler_version})", entry.display());
    for exercise in exercises {
        let NativeCheck::TypeScript {
            harness,
            config,
            api,
        } = exercise.check
        else {
            return Err(Outcome::Blocked("invalid TypeScript selector".into()));
        };
        let syntax = output(
            Command::new(&node)
                .arg("--check")
                .arg(directory.join(harness)),
        )?;
        if !syntax.status.success() {
            diagnostics(&syntax);
            return Err(Outcome::Blocked(
                "TypeScript check harness has invalid JavaScript syntax".into(),
            ));
        }
        let scratch = Scratch::new("typescript")?;
        let report_path = scratch.path.join("report.json");
        let stdout_path = scratch.path.join("stdout");
        let stdout = fs::OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&stdout_path)
            .map_err(|error| {
                Outcome::Blocked(format!("cannot create TypeScript stdout capture: {error}"))
            })?;
        let mut result = output(
            Command::new(&node)
                .current_dir(directory)
                .stdout(Stdio::from(stdout))
                .arg(directory.join(harness))
                .arg(&compiler)
                .arg(directory)
                .arg(directory.join(config))
                .arg(directory.join(exercise.file))
                .arg(directory.join(api))
                .arg(&scratch.path)
                .arg(&report_path),
        )?;
        result.stdout = fs::read(&stdout_path).map_err(|error| {
            Outcome::Indeterminate(format!("cannot read TypeScript stdout capture: {error}"))
        })?;
        diagnostics(&result);
        let report: Value = fs::read(&report_path)
            .ok()
            .and_then(|bytes| serde_json::from_slice(&bytes).ok())
            .ok_or_else(|| {
                Outcome::Indeterminate(format!(
                    "TypeScript produced no trustworthy private check report ({})",
                    result.status
                ))
            })?;
        if !result.status.success() {
            return Err(Outcome::Indeterminate(format!(
                "TypeScript harness exited unexpectedly ({})",
                result.status
            )));
        }
        let reason = report["reason"]
            .as_str()
            .filter(|reason| !reason.is_empty())
            .ok_or_else(|| Outcome::Indeterminate("TypeScript report has no reason".into()))?;
        let stage = report["stage"]
            .as_str()
            .filter(|stage| matches!(*stage, "compiler" | "config" | "compile" | "runtime"))
            .ok_or_else(|| Outcome::Indeterminate("TypeScript report has no valid stage".into()))?;
        let expected_output = result.stdout == b"Hello, World!\n";
        if stage == "runtime" && !expected_output {
            eprintln!(
                "Your output: {:?}\nExpected output: {:?}",
                String::from_utf8_lossy(&result.stdout),
                "Hello, World!\n"
            );
        }
        let outcome = match report["outcome"].as_str() {
            Some("passed") if stage == "runtime" && expected_output => Outcome::Passed,
            Some("passed") if stage == "runtime" => Outcome::AttemptFailed,
            Some("failed") => Outcome::AttemptFailed,
            Some("blocked") => Outcome::Blocked(reason.into()),
            _ => Outcome::Indeterminate(reason.into()),
        };
        if outcome != Outcome::Passed {
            return Ok(outcome);
        }
    }
    Ok(Outcome::Passed)
}
