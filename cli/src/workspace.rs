use std::fs::{self, OpenOptions};
use std::io::{self, Write};
use std::path::{Component, Path, PathBuf};

use crate::model::{Language, Outcome};

// Check every component, not just canonical containment: an in-root symlink can
// otherwise redirect a later exclusive create or native tool invocation.
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
    for name in [workspace.starter, workspace.answers, "README.md"]
        .into_iter()
        .chain(workspace.inputs.iter().copied())
    {
        let path = safe_path(root, &Path::new(workspace.directory).join(name))?;
        if name != "target" && path.exists() && !path.is_file() {
            return Err(Outcome::Blocked(format!(
                "expected a file: {}",
                path.display()
            )));
        }
    }
    Ok(directory)
}

pub fn prevalidate_start(root: &Path, language: Language) -> Result<(), Outcome> {
    let directory = validate(root, language)?;
    let workspace = language.workspace();
    if !directory.join(workspace.answers).is_file() {
        let starter = directory.join(workspace.starter);
        fs::read(&starter)
            .map_err(|error| Outcome::Blocked(format!("{}: {error}", starter.display())))?;
    }
    Ok(())
}

pub fn start(root: &Path, language: Language) -> Result<(), Outcome> {
    let directory = validate(root, language)?;
    let workspace = language.workspace();
    let answer = directory.join(workspace.answers);
    if answer.is_file() {
        println!("Preserved {}", answer.display());
        return Ok(());
    }
    let starter = directory.join(workspace.starter);
    let bytes = fs::read(&starter)
        .map_err(|error| Outcome::Blocked(format!("{}: {error}", starter.display())))?;
    match OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&answer)
    {
        Ok(mut file) => {
            file.write_all(&bytes)
                .map_err(|error| Outcome::Blocked(format!("{}: {error}", answer.display())))?;
            println!("Created {}", answer.display());
        }
        Err(error) if error.kind() == io::ErrorKind::AlreadyExists => {
            validate(root, language)?;
            if !answer.is_file() {
                return Err(Outcome::Blocked(format!(
                    "expected a file: {}",
                    answer.display()
                )));
            }
            println!("Preserved {}", answer.display());
        }
        Err(error) => return Err(Outcome::Blocked(format!("{}: {error}", answer.display()))),
    }
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
