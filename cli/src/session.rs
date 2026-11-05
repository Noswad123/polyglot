use std::io::{self, Write};

use crate::model::{Exercise, Language, Outcome, CATALOG};
use crate::workflow::{self, Context};

const HELP: &str = "Commands: Enter/check/c, hint/h, prompt, next/n, previous/p, list/l,
language python|rust, help/?, quit/q.
Edit and save the answer in your own editor, then check. Next always rechecks.";

fn read_line(prompt: &str) -> Result<Option<String>, Outcome> {
    print!("{prompt}");
    io::stdout()
        .flush()
        .map_err(|error| Outcome::Blocked(format!("stdout: {error}")))?;
    let mut line = String::new();
    match io::stdin().read_line(&mut line) {
        Ok(0) => Ok(None),
        Ok(_) => Ok(Some(line.trim().to_owned())),
        Err(error) => Err(Outcome::Blocked(format!("stdin: {error}"))),
    }
}

pub fn choose_language() -> Result<Option<&'static Exercise>, Outcome> {
    while let Some(line) = read_line("Choose a language (1: python, 2: rust; q: quit): ")? {
        let language = match line.as_str() {
            "q" | "quit" => return Ok(None),
            "1" => Some(Language::Python),
            "2" => Some(Language::Rust),
            value => Language::parse(value),
        };
        if let Some(language) = language {
            return Ok(CATALOG.iter().find(|e| e.language == language));
        }
        println!("Invalid language. Choose python/rust or 1/2.");
    }
    Ok(None)
}

pub fn run(context: &Context, initial: &'static Exercise) -> Result<(), Outcome> {
    context.start(initial)?;
    let mut track: Vec<_> = CATALOG
        .iter()
        .filter(|e| e.language == initial.language)
        .collect();
    let mut index = track.iter().position(|e| e.id == initial.id).unwrap();
    context.show(initial, Some((index, track.len())));
    println!("{HELP}");
    while let Some(line) = read_line("practice> ")? {
        let current = track[index];
        let target = match line.as_str() {
            "q" | "quit" => break,
            "" | "check" | "c" => {
                println!("{}", context.check(&[current]));
                continue;
            }
            "hint" | "h" => {
                println!("Hint: {}", current.hint);
                continue;
            }
            "prompt" => {
                println!("Prompt: {}", current.prompt);
                continue;
            }
            "next" | "n" => {
                let outcome = context.check(&[current]);
                println!("{outcome}");
                if outcome != Outcome::Passed {
                    continue;
                }
                if index + 1 == track.len() {
                    println!("End of track");
                    continue;
                }
                track[index + 1]
            }
            "previous" | "p" => {
                if index == 0 {
                    println!("Already at the first exercise");
                    continue;
                }
                track[index - 1]
            }
            "list" | "l" => {
                workflow::catalog(Some(current.language));
                continue;
            }
            "help" | "?" => {
                println!("{HELP}");
                continue;
            }
            _ => {
                let words: Vec<_> = line.split_whitespace().collect();
                if words.first() == Some(&"language") {
                    let language = match words.as_slice() {
                        [_, value] => Language::parse(value),
                        _ => None,
                    };
                    let Some(language) = language else {
                        println!("Blocked: usage: language python|rust");
                        continue;
                    };
                    CATALOG.iter().find(|e| e.language == language).unwrap()
                } else {
                    println!("Unknown command. Type help for commands.");
                    continue;
                }
            }
        };
        // Commit selection only after exclusive preparation succeeds.
        if let Err(outcome) = context.start(target) {
            println!("{outcome}");
            continue;
        }
        track = CATALOG
            .iter()
            .filter(|e| e.language == target.language)
            .collect();
        index = track.iter().position(|e| e.id == target.id).unwrap();
        context.show(target, Some((index, track.len())));
    }
    Ok(())
}
