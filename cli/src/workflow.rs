use std::path::PathBuf;

use crate::model::{Exercise, Language, Outcome, CATALOG};
use crate::{adapters, workspace};

pub struct Context {
    pub root: PathBuf,
    pub python: Option<PathBuf>,
    pub cargo: Option<PathBuf>,
}

impl Context {
    pub fn resolve(mut self) -> Result<Self, Outcome> {
        self.root = self
            .root
            .canonicalize()
            .map_err(|error| Outcome::Blocked(format!("root {}: {error}", self.root.display())))?;
        if !self.root.is_dir() {
            return Err(Outcome::Blocked("root must be a directory".into()));
        }
        Ok(self)
    }

    pub fn start(&self, exercise: &Exercise) -> Result<(), Outcome> {
        workspace::start(&self.root, exercise.language)
    }

    pub fn show(&self, exercise: &Exercise, position: Option<(usize, usize)>) {
        match position {
            Some((index, count)) => println!("Exercise: {} ({}/{count})", exercise.id, index + 1),
            None => println!("Exercise: {}", exercise.id),
        }
        println!("Title: {}", exercise.title);
        println!(
            "Answer: {}",
            self.root
                .join(exercise.language.workspace().directory)
                .join(exercise.language.workspace().answers)
                .display()
        );
        println!("Prompt: {}", exercise.prompt);
    }

    pub fn check(&self, exercises: &[&Exercise]) -> Outcome {
        let language = exercises[0].language;
        let directory = match workspace::validate(&self.root, language) {
            Ok(directory) => directory,
            Err(outcome) => return outcome,
        };
        if !directory.join(language.workspace().answers).is_file() {
            return Outcome::Blocked(format!("no attempt; run start {} first", exercises[0].id));
        }
        adapters::check(
            &self.root,
            &directory,
            language,
            exercises,
            self.python.as_deref(),
            self.cargo.as_deref(),
        )
    }
}

pub fn catalog(language: Option<Language>) {
    for exercise in CATALOG
        .iter()
        .filter(|e| language.is_none_or(|l| l == e.language))
    {
        println!(
            "{}\t{}\tPrompt/hints: {}/README.md",
            exercise.id,
            exercise.title,
            exercise.language.workspace().directory
        );
    }
}
