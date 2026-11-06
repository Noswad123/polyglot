mod adapters;
mod git;
mod model;
mod reset;
mod session;
mod workflow;
mod workspace;

use std::path::PathBuf;
use std::process::ExitCode;

use model::{Exercise, Language, Outcome, CATALOG};
use workflow::Context;

const HELP: &str = "polyglot [--root PATH] [--python PATH] [--cargo PATH] COMMAND

Commands:
  list [--language python|rust]
  start ID
  reset ID
  check ID|python|rust
  show ID
  hint ID
  practice [python|rust|ID]

IDs: python/hello, python/find_in_string, python/length_of_last_word, rust/hello
Global options must precede the command. --help shows this help.
Start selects existing exercise files. Check never creates exercise files.
Reset restores one exercise from committed main after confirmation.
Start requires a non-main Git branch. Practice creates one from clean main.
";

fn select(value: &str, track: bool) -> Result<Vec<&'static Exercise>, Outcome> {
    let exercises: Vec<_> = CATALOG
        .iter()
        .filter(|exercise| {
            exercise.id == value || (track && Language::parse(value) == Some(exercise.language))
        })
        .collect();
    if exercises.is_empty() {
        Err(Outcome::Blocked(format!(
            "unknown exercise or track: {value}"
        )))
    } else {
        Ok(exercises)
    }
}

fn run() -> Result<(), Outcome> {
    let mut args = std::env::args_os().skip(1).peekable();
    let mut options = Context {
        root: PathBuf::from(env!("CARGO_MANIFEST_DIR")),
        python: None,
        cargo: None,
    };
    while let Some(arg) = args.peek() {
        if arg == "--help" || arg == "-h" {
            print!("{HELP}");
            return Ok(());
        }
        let destination = match arg.to_str() {
            Some("--root") => &mut options.root,
            Some("--python") => options.python.get_or_insert_with(PathBuf::new),
            Some("--cargo") => options.cargo.get_or_insert_with(PathBuf::new),
            _ => break,
        };
        let flag = args.next().unwrap();
        *destination = args
            .next()
            .map(PathBuf::from)
            .filter(|p| !p.as_os_str().is_empty())
            .ok_or_else(|| Outcome::Blocked(format!("{} requires PATH", flag.to_string_lossy())))?;
    }
    let args: Vec<_> = args
        .map(|arg| {
            arg.into_string()
                .map_err(|_| Outcome::Blocked("command arguments must be UTF-8".into()))
        })
        .collect::<Result<_, _>>()?;
    let Some(command) = args.first() else {
        return Err(Outcome::Blocked(format!("a command is required\n{HELP}")));
    };
    // Validate selection before touching any workspace or launching tools.
    match command.as_str() {
        "list" => {
            let language = match args.as_slice() {
                [_] => None,
                [_, flag, value] if flag == "--language" => Some(
                    Language::parse(value)
                        .ok_or_else(|| Outcome::Blocked(format!("unknown language: {value}")))?,
                ),
                _ => {
                    return Err(Outcome::Blocked(
                        "usage: list [--language python|rust]".into(),
                    ))
                }
            };
            workflow::catalog(language);
            Ok(())
        }
        "practice" => {
            let initial = match args.as_slice() {
                [_] => session::choose_language()?,
                [_, value] => Some(select(value, true)?[0]),
                _ => return Err(Outcome::Blocked("usage: practice [python|rust|ID]".into())),
            };
            let Some(initial) = initial else {
                return Ok(());
            };
            session::run(&options.resolve()?, initial)
        }
        "start" | "reset" | "check" | "show" | "hint" => {
            if args.len() != 2 {
                return Err(Outcome::Blocked(format!(
                    "usage: {command} {}",
                    if command == "check" {
                        "ID|python|rust"
                    } else {
                        "ID"
                    }
                )));
            }
            let exercises = select(&args[1], command == "check")?;
            if command == "hint" {
                println!("Hint: {}", exercises[0].hint);
                return Ok(());
            }
            let context = options.resolve()?;
            let language = exercises[0].language;
            if command == "reset" {
                reset::run(&context.root, exercises[0])?;
                return Ok(());
            }
            if command == "show" {
                context.show(exercises[0], None);
                return Ok(());
            }
            if command == "start" {
                context.start(exercises[0])?;
                println!(
                    "Prompt/hints: {}/README.md",
                    context.root.join(language.workspace().directory).display()
                );
                return Ok(());
            }
            let outcome = context.check(&exercises);
            match outcome {
                Outcome::Passed => {
                    println!("Passed");
                    Ok(())
                }
                other => Err(other),
            }
        }
        _ => Err(Outcome::Blocked(format!("unknown command: {command}"))),
    }
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(outcome) => {
            eprintln!("{outcome}");
            ExitCode::from(outcome.code())
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn selection_is_exact_and_tracks_are_check_only() {
        assert_eq!(select("python", true).unwrap().len(), 3);
        assert_eq!(select("rust/hello", false).unwrap().len(), 1);
        for value in ["python", "../rust/hello", "hello", "python/hello/", ""] {
            assert!(select(value, false).is_err());
        }
    }
}
