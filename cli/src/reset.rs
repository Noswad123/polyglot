#[cfg(any(target_os = "macos", target_os = "linux"))]
use std::fs::Permissions;
#[cfg(any(target_os = "macos", target_os = "linux"))]
use std::io::{self, Write};
use std::path::Path;
#[cfg(any(target_os = "macos", target_os = "linux"))]
use std::path::PathBuf;
#[cfg(any(target_os = "macos", target_os = "linux"))]
use std::time::SystemTime;

use crate::model::{Exercise, Outcome};
#[cfg(any(target_os = "macos", target_os = "linux"))]
use crate::{git, workspace};

#[cfg(any(target_os = "macos", target_os = "linux"))]
mod native;
#[cfg(any(target_os = "macos", target_os = "linux"))]
use native::snapshot;

#[cfg(any(target_os = "macos", target_os = "linux"))]
struct Snapshot {
    bytes: Vec<u8>,
    modified: SystemTime,
    permissions: Permissions,
}

fn blocked(error: impl std::fmt::Display) -> Outcome {
    Outcome::Blocked(format!("reset: {error}"))
}

#[cfg(any(target_os = "macos", target_os = "linux"))]
fn revalidate(
    root: &Path,
    exercise: &Exercise,
    relative: &Path,
    branch: &str,
    initial: &Option<Snapshot>,
) -> Result<(), Outcome> {
    if git::practice_branch(root)? != branch {
        return Err(blocked(
            "branch changed during reset; nothing was overwritten",
        ));
    }
    validate_paths(root, exercise)?;
    let current = snapshot(root, relative)?;
    let unchanged = match (initial, current) {
        (None, None) => true,
        (Some(before), Some(after)) => {
            before.bytes == after.bytes
                && before.modified == after.modified
                && before.permissions == after.permissions
        }
        _ => false,
    };
    if !unchanged {
        return Err(blocked(
            "exercise file changed during reset; nothing was overwritten",
        ));
    }
    Ok(())
}

#[cfg(any(target_os = "macos", target_os = "linux"))]
fn validate_paths(root: &Path, exercise: &Exercise) -> Result<PathBuf, Outcome> {
    let relative = Path::new(exercise.language.workspace().directory).join(exercise.file);
    let path = workspace::safe_path(root, &relative)?;
    for input in exercise.language.workspace().inputs {
        let common = workspace::safe_path(
            root,
            &Path::new(exercise.language.workspace().directory).join(input),
        )?;
        if common.exists()
            && ((*input == "target" && !common.is_dir())
                || (*input != "target" && !common.is_file()))
        {
            return Err(blocked(format!(
                "invalid common workspace path: {}",
                common.display()
            )));
        }
    }
    Ok(path)
}

#[cfg(not(any(target_os = "macos", target_os = "linux")))]
pub fn run(_root: &Path, _exercise: &Exercise) -> Result<bool, Outcome> {
    Err(blocked(
        "safe reset is supported only on macOS and Linux; no filesystem changes were made",
    ))
}

#[cfg(any(target_os = "macos", target_os = "linux"))]
pub fn run(root: &Path, exercise: &Exercise) -> Result<bool, Outcome> {
    let branch = git::practice_branch(root)?;
    let relative = Path::new(exercise.language.workspace().directory).join(exercise.file);
    validate_paths(root, exercise)?;
    let (oid, baseline) = git::reset_baseline(root, &relative)?;
    let initial = snapshot(root, &relative)?;
    println!("Reset baseline: refs/heads/main at {oid}");
    if initial
        .as_ref()
        .is_some_and(|source| source.bytes == baseline)
    {
        println!("Already pristine");
        return Ok(false);
    }
    print!("Reset {}? [y/N]:", exercise.id);
    io::stdout().flush().map_err(blocked)?;
    let mut answer = String::new();
    io::stdin().read_line(&mut answer).map_err(blocked)?;
    if !matches!(answer.trim().to_ascii_lowercase().as_str(), "y" | "yes") {
        println!("Reset cancelled");
        return Ok(false);
    }
    revalidate(root, exercise, &relative, &branch, &initial)?;
    native::install(root, &relative, &baseline, &initial, || {
        revalidate(root, exercise, &relative, &branch, &initial)
    })?;
    println!(
        "Reset: {}. Staged content was not reset; the index is unchanged.",
        exercise.id
    );
    Ok(true)
}
