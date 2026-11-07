mod go;
mod python;
mod rust;
mod shell;
mod support;
mod typescript;

use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::process::{Command, Output};

use crate::model::{Exercise, Language, Outcome};

#[derive(Default)]
pub(crate) struct Tools {
    pub(crate) python: Option<PathBuf>,
    pub(crate) cargo: Option<PathBuf>,
    pub(crate) node: Option<PathBuf>,
    pub(crate) tsc: Option<PathBuf>,
    pub(crate) go: Option<PathBuf>,
    pub(crate) bash: Option<PathBuf>,
    pub(crate) lua: Option<PathBuf>,
}

pub fn check(
    root: &Path,
    directory: &Path,
    language: Language,
    exercises: &[&Exercise],
    tools: &Tools,
) -> Outcome {
    let result = match language {
        Language::Python => python::check(root, directory, exercises, tools.python.as_deref()),
        Language::Rust => rust::check(root, directory, exercises, tools.cargo.as_deref()),
        Language::TypeScript => typescript::check(root, directory, exercises, tools),
        Language::Go => go::check(root, directory, exercises, tools),
        Language::Bash | Language::Lua => shell::check(root, directory, exercises, tools),
    };
    result.unwrap_or_else(|outcome| outcome)
}

fn tool(path: &Path) -> Result<PathBuf, Outcome> {
    if path.is_absolute() || path.components().count() > 1 {
        let absolute = std::env::current_dir()
            .map_err(|error| Outcome::Blocked(error.to_string()))?
            .join(path);
        if absolute.is_file() {
            return Ok(absolute);
        }
        return Err(Outcome::Blocked(format!(
            "tool not found: {}",
            absolute.display()
        )));
    }
    for directory in std::env::split_paths(&std::env::var_os("PATH").unwrap_or_default()) {
        let candidate = directory.join(path);
        if candidate.is_file() {
            // Preserve the executable name and venv location: cargo may be a
            // rustup proxy, and resolving Python's symlink loses its venv.
            return std::env::current_dir()
                .map(|cwd| cwd.join(candidate))
                .map_err(|error| Outcome::Blocked(error.to_string()));
        }
    }
    Err(Outcome::Blocked(format!(
        "tool not found: {}",
        path.display()
    )))
}

fn output(command: &mut Command) -> Result<Output, Outcome> {
    let output = command.output().map_err(|error| {
        Outcome::Blocked(format!(
            "could not run {}: {error}",
            command.get_program().to_string_lossy()
        ))
    })?;
    if output.status.code().is_none() {
        diagnostics(&output);
        return Err(Outcome::Indeterminate(format!(
            "native process terminated: {}",
            output.status
        )));
    }
    Ok(output)
}

fn diagnostics(output: &Output) {
    let _ = io::stdout().write_all(&output.stdout);
    let _ = io::stdout().flush();
    let _ = io::stderr().write_all(&output.stderr);
}
