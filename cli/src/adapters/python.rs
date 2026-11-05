use std::fs::{self, OpenOptions};
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::atomic::{AtomicU64, Ordering};

use serde_json::Value;

use super::{diagnostics, output, tool};
use crate::model::{Exercise, NativeCheck, Outcome};

const HELPER: &str = include_str!("python_check.py");

struct Report(PathBuf);

impl Report {
    fn new() -> Result<Self, Outcome> {
        static SERIAL: AtomicU64 = AtomicU64::new(0);
        for _ in 0..100 {
            let path = std::env::temp_dir().join(format!(
                "polyglot-report-{}-{}.json",
                std::process::id(),
                SERIAL.fetch_add(1, Ordering::Relaxed)
            ));
            match OpenOptions::new().write(true).create_new(true).open(&path) {
                Ok(_) => return Ok(Self(path)),
                Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => continue,
                Err(error) => {
                    return Err(Outcome::Blocked(format!(
                        "cannot create check report: {error}"
                    )))
                }
            }
        }
        Err(Outcome::Blocked("cannot allocate check report".into()))
    }
}

impl Drop for Report {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.0);
    }
}

pub fn check(
    root: &Path,
    directory: &Path,
    exercises: &[&Exercise],
    override_path: Option<&Path>,
) -> Result<Outcome, Outcome> {
    let selected = if let Some(path) = override_path {
        path.to_path_buf()
    } else {
        let unix = root.join(".venv/bin/python");
        let windows = root.join(".venv/Scripts/python.exe");
        if fs::symlink_metadata(&unix).is_ok() {
            unix
        } else if fs::symlink_metadata(&windows).is_ok() {
            windows
        } else {
            PathBuf::from("python3")
        }
    };
    let interpreter = tool(&selected)?;
    let version = output(Command::new(&interpreter).args([
        "-B", "-c", "import json,sys; print(json.dumps({'version': list(sys.version_info[:3]), 'executable': sys.executable}))",
    ]).env("PYTHONDONTWRITEBYTECODE", "1"))?;
    if !version.status.success() {
        diagnostics(&version);
        return Err(Outcome::Blocked(format!(
            "Python version probe failed ({})",
            version.status
        )));
    }
    let info: Value = serde_json::from_slice(&version.stdout)
        .map_err(|_| Outcome::Blocked("invalid Python version response".into()))?;
    let major = info["version"][0].as_u64().unwrap_or(0);
    let minor = info["version"][1].as_u64().unwrap_or(0);
    if major != 3 || minor < 11 {
        return Err(Outcome::Blocked("Python >=3.11 is required".into()));
    }
    println!(
        "Python: {} ({}.{}.{})",
        interpreter.display(),
        major,
        minor,
        info["version"][2]
    );
    let report = Report::new()?;
    let mut command = Command::new(&interpreter);
    command
        .current_dir(directory)
        .env("PYTHONDONTWRITEBYTECODE", "1")
        .args(["-B", "-c", HELPER])
        .arg(&report.0);
    for exercise in exercises {
        let NativeCheck::Python(selector) = exercise.check else {
            return Err(Outcome::Blocked("invalid Python selector".into()));
        };
        command.arg(selector);
    }
    let result = output(&mut command)?;
    diagnostics(&result);
    let report: Value = fs::read(&report.0)
        .ok()
        .and_then(|bytes| serde_json::from_slice(&bytes).ok())
        .ok_or_else(|| {
            Outcome::Indeterminate(format!(
                "Python produced no trustworthy check report ({})",
                result.status
            ))
        })?;
    let state = report["outcome"].as_str().unwrap_or("");
    if !result.status.success() {
        return Err(Outcome::Indeterminate(format!(
            "Python helper exited unexpectedly ({})",
            result.status
        )));
    }
    let reason = report["reason"]
        .as_str()
        .unwrap_or("unknown Python check behavior")
        .to_string();
    Ok(match state {
        "passed" if report["ran"].as_u64() == Some(exercises.len() as u64) => Outcome::Passed,
        "failed" => Outcome::AttemptFailed,
        "blocked" => Outcome::Blocked(reason),
        _ => Outcome::Indeterminate(reason),
    })
}
