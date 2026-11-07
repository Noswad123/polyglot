use std::fs::{self, OpenOptions};
use std::path::Path;
use std::process::Command;

use super::support::Scratch;
use super::{diagnostics, output, tool, Tools};
use crate::model::{Exercise, NativeCheck, Outcome};

pub fn check(
    _root: &Path,
    directory: &Path,
    exercises: &[&Exercise],
    tools: &Tools,
) -> Result<Outcome, Outcome> {
    for exercise in exercises {
        let (bash, harness, executable) = match exercise.check {
            NativeCheck::Bash { harness } => (
                true,
                harness,
                tools.bash.as_deref().unwrap_or(Path::new("bash")),
            ),
            NativeCheck::Lua { harness } => (
                false,
                harness,
                tools.lua.as_deref().unwrap_or(Path::new("lua")),
            ),
            _ => return Err(Outcome::Blocked("invalid shell selector".into())),
        };
        let executable = tool(executable)?;
        let command = || {
            let mut command = Command::new(&executable);
            command
                .env_remove("BASH_ENV")
                .env_remove("ENV")
                .env_remove("SHELLOPTS");
            if bash {
                command.args(["--noprofile", "--norc"]);
            } else {
                command.env_remove("LUA_INIT");
                for version in ["5_1", "5_2", "5_3", "5_4", "5_5"] {
                    command.env_remove(format!("LUA_INIT_{version}"));
                }
            }
            command
        };
        let version = if bash {
            output(command().args([
                "-c",
                "printf '%s.%s' \"${BASH_VERSINFO[0]}\" \"${BASH_VERSINFO[1]}\"",
            ]))?
        } else {
            output(command().args(["-e", "io.write(_VERSION)"]))?
        };
        let version_text = String::from_utf8_lossy(&version.stdout);
        let numbers: Vec<_> = version_text
            .trim_start_matches("Lua ")
            .trim()
            .split('.')
            .filter_map(|v| v.parse::<u32>().ok())
            .collect();
        let minimum = if bash { (3, 2) } else { (5, 1) };
        if !version.status.success() || numbers.len() < 2 || (numbers[0], numbers[1]) < minimum {
            diagnostics(&version);
            return Err(Outcome::Blocked(format!(
                "{} >={}.{} is required",
                if bash { "Bash" } else { "Lua" },
                minimum.0,
                minimum.1
            )));
        }
        let scratch = Scratch::new(if bash { "bash" } else { "lua" })?;
        let source = scratch
            .path
            .join(if bash { "hello.sh" } else { "hello.lua" });
        let selected_harness = scratch
            .path
            .join(if bash { "check.sh" } else { "check.lua" });
        for (from, to) in [
            (directory.join(exercise.file), &source),
            (directory.join(harness), &selected_harness),
        ] {
            fs::copy(&from, to)
                .map_err(|error| Outcome::Blocked(format!("copy {}: {error}", from.display())))?;
        }
        let preflight = if bash {
            output(command().arg("-n").arg(&selected_harness))?
        } else {
            output(command().args(["-e", "local f,e=loadfile(os.getenv('POLYGLOT_HARNESS')); if not f then io.stderr:write(e, '\\n'); os.exit(1) end"]).env("POLYGLOT_HARNESS", &selected_harness))?
        };
        if !preflight.status.success() {
            diagnostics(&preflight);
            return Err(Outcome::Blocked(
                "selected test harness has invalid syntax".into(),
            ));
        }
        println!(
            "Checking {} (isolated copy: {})",
            directory.join(exercise.file).display(),
            source.display()
        );
        let report = scratch.path.join("report");
        let capture = scratch.path.join("stdout");
        let mut options = OpenOptions::new();
        options.write(true).create_new(true);
        #[cfg(unix)]
        {
            use std::os::unix::fs::OpenOptionsExt;
            options.mode(0o600);
        }
        let capture_file = options.open(&capture).map_err(|error| {
            Outcome::Blocked(format!("could not create private stdout capture: {error}"))
        })?;
        let mut native = command();
        native
            .current_dir(&scratch.path)
            .arg(&selected_harness)
            .arg(&source)
            .arg(&report);
        if bash {
            native.arg(&capture);
        } else {
            // A regular stdout file lets Lua measure load-time writes without
            // replacing print/io.write or breaking captured stdout handles.
            native.stdout(capture_file);
        }
        let mut result = output(&mut native)?;
        if !bash {
            result.stdout = fs::read(&capture).map_err(|error| {
                Outcome::Indeterminate(format!("could not read Lua stdout capture: {error}"))
            })?;
        }
        diagnostics(&result);
        let state = fs::read_to_string(&report).map_err(|_| {
            Outcome::Indeterminate(format!(
                "native check produced no completion report ({})",
                result.status
            ))
        })?;
        // Bash keeps process-level writes separate from the source/function
        // handle, including writes made by EXIT traps after the report.
        let process_output_empty = !bash || result.stdout.is_empty();
        if bash {
            result.stdout = fs::read(&capture).map_err(|error| {
                Outcome::Indeterminate(format!("could not read Bash stdout capture: {error}"))
            })?;
        }
        let output_matches = process_output_empty && result.stdout == b"Hello, World!\n";
        if !output_matches && matches!(state.as_str(), "passed\n" | "failed\n") {
            eprintln!(
                "Your output: \"{}\"\nExpected output: \"{}\"",
                result.stdout.escape_ascii(),
                b"Hello, World!\n".escape_ascii()
            );
        }
        match state.as_str() {
            "blocked\n" => return Ok(Outcome::Blocked("Lua stdout capture is unavailable; use a Lua >=5.1 runtime with regular-file stdout flush/seek support".into())),
            "failed\n" => return Ok(Outcome::AttemptFailed),
            "passed\n" if result.status.success() => {
                if !output_matches {
                    return Ok(Outcome::AttemptFailed);
                }
            }
            _ => {
                return Err(Outcome::Indeterminate(format!(
                    "unexpected native completion report ({})",
                    result.status
                )))
            }
        }
    }
    Ok(Outcome::Passed)
}
