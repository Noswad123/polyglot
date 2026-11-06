use std::fs;
use std::io;
use std::path::{Component, Path, PathBuf};

use crate::model::{Exercise, Language, NativeCheck, Outcome};

// Check every component: even an in-root symlink can redirect a later write.
pub fn safe_path(root: &Path, relative: &Path) -> Result<PathBuf, Outcome> {
    let mut path = root.to_path_buf();
    for component in relative.components() {
        let Component::Normal(name) = component else {
            return Err(Outcome::Blocked(format!(
                "invalid workspace path: {}",
                relative.display()
            )));
        };
        path.push(name);
        match fs::symlink_metadata(&path) {
            Ok(metadata) if metadata.file_type().is_symlink() => {
                return Err(Outcome::Blocked(format!(
                    "symlink is not allowed: {}",
                    path.display()
                )));
            }
            Ok(_) => {}
            Err(error) if error.kind() == io::ErrorKind::NotFound => {}
            Err(error) => return Err(Outcome::Blocked(format!("{}: {error}", path.display()))),
        }
    }
    Ok(path)
}

pub fn validate(root: &Path, language: Language) -> Result<PathBuf, Outcome> {
    let workspace = language.workspace();
    let directory = safe_path(root, Path::new(workspace.directory))?;
    if !directory.is_dir() {
        return Err(Outcome::Blocked(format!(
            "workspace is missing: {}",
            directory.display()
        )));
    }
    for name in workspace.inputs {
        let path = safe_path(root, &Path::new(workspace.directory).join(name))?;
        if *name == "target" {
            if path.exists() && !path.is_dir() {
                return Err(Outcome::Blocked(format!(
                    "expected a directory: {}",
                    path.display()
                )));
            }
        } else if !path.is_file() {
            return Err(Outcome::Blocked(format!(
                "required workspace file is missing or not regular: {}",
                path.display()
            )));
        }
    }
    Ok(directory)
}

pub fn prevalidate_start(root: &Path, exercise: &Exercise) -> Result<(), Outcome> {
    validate(root, exercise.language)?;
    let relative = Path::new(exercise.language.workspace().directory).join(exercise.file);
    let path = safe_path(root, &relative)?;
    if !path.is_file() {
        return Err(Outcome::Blocked(format!("exercise file is missing or not regular: {}. Use `polyglot reset {}` after committing a reviewed pristine exercise on main first.", path.display(), exercise.id)));
    }
    if let NativeCheck::Python(selector) = exercise.check {
        let module = selector.rsplit_once(".PracticeTests.").unwrap().0;
        let harness = format!("{}.py", module.replace('.', "/"));
        let path = safe_path(
            root,
            &Path::new(exercise.language.workspace().directory).join(harness),
        )?;
        if !path.is_file() {
            return Err(Outcome::Blocked(format!(
                "selected test harness is missing or not regular: {}",
                path.display()
            )));
        }
    }
    Ok(())
}

pub fn start(root: &Path, exercise: &Exercise) -> Result<(), Outcome> {
    prevalidate_start(root, exercise)?;
    println!(
        "Exercise file: {}",
        root.join(exercise.language.workspace().directory)
            .join(exercise.file)
            .display()
    );
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_paths_that_can_escape_root() {
        for path in ["../answers.rs", "/tmp/answers.rs", "practice/../answers.rs"] {
            assert!(safe_path(Path::new("/"), Path::new(path)).is_err());
        }
    }
}
