use std::path::Path;
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

use crate::model::{Language, Outcome};

pub fn raw(root: &Path, args: &[&str]) -> Result<Vec<u8>, Outcome> {
    let mut command = Command::new("git");
    command.arg("-C").arg(root).args(args);
    // An inherited Git context must not redirect --root to another repository.
    for name in [
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_COMMON_DIR",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_NAMESPACE",
        "GIT_IMPLICIT_WORK_TREE",
        "GIT_SHALLOW_FILE",
        "GIT_CONFIG",
        "GIT_CONFIG_COUNT",
        "GIT_CONFIG_PARAMETERS",
    ] {
        command.env_remove(name);
    }
    let output = command
        .env("GIT_OPTIONAL_LOCKS", "0")
        .env("GIT_NO_REPLACE_OBJECTS", "1")
        .output()
        .map_err(|error| Outcome::Blocked(format!("could not run Git: {error}")))?;
    if !output.status.success() {
        return Err(Outcome::Blocked(format!(
            "git {} failed ({}): {}",
            args.join(" "),
            output.status,
            String::from_utf8_lossy(&output.stderr).trim()
        )));
    }
    Ok(output.stdout)
}

fn run(root: &Path, args: &[&str]) -> Result<String, Outcome> {
    String::from_utf8(raw(root, args)?)
        .map(|text| text.trim_end_matches('\n').to_owned())
        .map_err(|_| Outcome::Blocked("Git output must be UTF-8".into()))
}

fn branch(root: &Path) -> Result<String, Outcome> {
    if run(root, &["rev-parse", "--is-bare-repository"])? != "false" {
        return Err(Outcome::Blocked(
            "practice requires a non-bare Git checkout or worktree".into(),
        ));
    }
    let top = run(root, &["rev-parse", "--show-toplevel"])?;
    let top = Path::new(&top)
        .canonicalize()
        .map_err(|error| Outcome::Blocked(format!("Git top-level: {error}")))?;
    let root = root
        .canonicalize()
        .map_err(|error| Outcome::Blocked(format!("root: {error}")))?;
    if top != root {
        return Err(Outcome::Blocked(
            "root must be the exact top-level of a Git checkout or worktree".into(),
        ));
    }
    run(&root, &["rev-parse", "--verify", "HEAD^{commit}"]).map_err(|_| {
        Outcome::Blocked("practice requires a committed HEAD; unborn HEAD is not supported".into())
    })?;
    let reference = run(&root, &["symbolic-ref", "--quiet", "HEAD"]).map_err(|_| {
        Outcome::Blocked("practice requires a named branch; detached HEAD is not supported".into())
    })?;
    reference
        .strip_prefix("refs/heads/")
        .map(str::to_owned)
        .ok_or_else(|| Outcome::Blocked("HEAD must refer to a local branch".into()))
}

pub fn require_practice_branch(root: &Path) -> Result<(), Outcome> {
    practice_branch(root).map(|_| ())
}

pub fn practice_branch(root: &Path) -> Result<String, Outcome> {
    let name = branch(root)?;
    if name == "main" {
        return Err(Outcome::Blocked(
            "main is protected. Run `polyglot practice` to automatically create a branch on clean main, or run `git switch -c practice/<name>` to safely carry dirty work."
                .into(),
        ));
    }
    Ok(name)
}

pub fn reset_baseline(root: &Path, relative: &Path) -> Result<(String, Vec<u8>), Outcome> {
    let unavailable = || {
        Outcome::Blocked(format!(
        "reset baseline is unavailable for {}. Commit the reviewed pristine exercise on main first (refs/heads/main); no working-tree or learner-HEAD fallback is used.", relative.display()
    ))
    };
    let oid = run(root, &["rev-parse", "--verify", "refs/heads/main^{commit}"])
        .map_err(|_| unavailable())?;
    let path = relative.to_str().ok_or_else(unavailable)?;
    let entry = raw(root, &["ls-tree", "-z", &oid, "--", path]).map_err(|_| unavailable())?;
    let entry = entry.strip_suffix(&[0]).ok_or_else(unavailable)?;
    let tab = entry
        .iter()
        .position(|byte| *byte == b'\t')
        .ok_or_else(unavailable)?;
    if &entry[tab + 1..] != path.as_bytes() {
        return Err(unavailable());
    }
    let header = std::str::from_utf8(&entry[..tab]).map_err(|_| unavailable())?;
    let fields: Vec<_> = header.split(' ').collect();
    if fields.len() != 3 || !matches!(fields[0], "100644" | "100755") || fields[1] != "blob" {
        return Err(unavailable());
    }
    let bytes = raw(root, &["cat-file", "blob", fields[2]]).map_err(|_| unavailable())?;
    Ok((oid, bytes))
}

pub fn prepare_practice(root: &Path, language: Language) -> Result<(), Outcome> {
    let branch = branch(root)?;
    if branch != "main" {
        println!("Using practice branch: {branch}");
        return Ok(());
    }
    if !run(root, &["status", "--porcelain=v1", "--untracked-files=all"])?.is_empty() {
        return Err(Outcome::Blocked(
            "main has tracked, staged, or untracked changes. Run `git switch -c practice/<name>` to safely carry dirty work, or make main clean before running `polyglot practice`. Nothing was stashed or reset."
                .into(),
        ));
    }
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|error| Outcome::Blocked(format!("system clock: {error}")))?
        .as_nanos();
    let name = format!("practice/{language}-{timestamp}-{}", std::process::id());
    run(root, &["switch", "-c", &name])?;
    println!("Created practice branch: {name}");
    Ok(())
}
