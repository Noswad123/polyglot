use std::fs;
use std::path::{Path, PathBuf};

use crate::model::{Exercise, Language, Outcome, Problem, QuestionStatus, CATALOG, PROBLEMS};
use crate::{adapters, git, workspace};

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
        self.question(exercise.problem)?;
        git::require_practice_branch(&self.root)?;
        workspace::start(&self.root, exercise)
    }

    pub fn question(&self, problem: &Problem) -> Result<String, Outcome> {
        if problem.question_status != QuestionStatus::Curated {
            return Err(Outcome::Blocked(format!(
                "question is not curated: {}",
                problem.id
            )));
        }
        self.read_question(problem)
    }

    fn read_question(&self, problem: &Problem) -> Result<String, Outcome> {
        let document = problem.question_doc.ok_or_else(|| {
            Outcome::Blocked(format!("question document is missing: {}", problem.id))
        })?;
        let path = workspace::safe_path(&self.root, Path::new(document))?;
        let metadata = fs::symlink_metadata(&path)
            .map_err(|error| Outcome::Blocked(format!("question {}: {error}", path.display())))?;
        if !metadata.is_file() {
            return Err(Outcome::Blocked(format!(
                "question is not a regular file: {}",
                path.display()
            )));
        }
        let body = fs::read_to_string(&path)
            .map_err(|error| Outcome::Blocked(format!("question {}: {error}", path.display())))?;
        if body.trim().is_empty() && problem.question_status == QuestionStatus::Curated {
            return Err(Outcome::Blocked(format!(
                "question is empty: {}",
                path.display()
            )));
        }
        Ok(body)
    }

    pub fn question_detail(&self, problem: &Problem) -> Result<(), Outcome> {
        let body = problem
            .question_doc
            .map(|_| self.read_question(problem))
            .transpose()?;
        println!(
            "Problem: {}\nTitle: {}\nQuestion: {}",
            problem.id, problem.title, problem.question_status
        );
        match problem.question_doc {
            Some(document) => println!("Question file: {}", self.root.join(document).display()),
            None => println!("Question file: missing (no shared question document registered)"),
        }
        let bindings = bindings(problem);
        println!(
            "Native bindings: {}",
            if bindings.is_empty() {
                "none".into()
            } else {
                bindings.join(", ")
            }
        );
        println!("Solutions (not all checked; not runnable exercise bindings):");
        if problem.references.is_empty() {
            println!("  none");
        }
        for reference in problem.references {
            println!("  {}: {}", reference.language, reference.path);
            if let Some(note) = reference.note {
                println!("    Note: {note}");
            }
        }
        if problem.question_status == QuestionStatus::Draft {
            println!("Warning: draft, not validated shared contract");
        }
        if let Some(body) = body {
            if body.trim().is_empty() {
                println!("Empty draft: the registered document has no question text yet.");
            } else {
                println!("Prompt:\n{body}");
            }
        }
        Ok(())
    }

    pub fn show(
        &self,
        exercise: &Exercise,
        position: Option<(usize, usize)>,
    ) -> Result<(), Outcome> {
        let question = self.question(exercise.problem)?;
        match position {
            Some((index, count)) => println!("Exercise: {} ({}/{count})", exercise.id, index + 1),
            None => println!("Exercise: {}", exercise.id),
        }
        println!("Title: {}", exercise.problem.title);
        println!(
            "Exercise file: {}",
            self.root
                .join(exercise.language.workspace().directory)
                .join(exercise.file)
                .display()
        );
        println!("Problem: {}", exercise.problem.id);
        println!(
            "Question file: {}",
            self.root
                .join(exercise.problem.question_doc.unwrap())
                .display()
        );
        println!("Prompt:\n{question}");
        println!("Language task: {}", exercise.prompt);
        Ok(())
    }

    pub fn check_practice(&self, exercises: &[&Exercise]) -> Outcome {
        match git::require_practice_branch(&self.root) {
            Ok(()) => self.check(exercises),
            Err(outcome) => outcome,
        }
    }

    pub fn check(&self, exercises: &[&Exercise]) -> Outcome {
        let language = exercises[0].language;
        let directory = match workspace::validate(&self.root, language) {
            Ok(directory) => directory,
            Err(outcome) => return outcome,
        };
        for exercise in exercises {
            if let Err(outcome) = workspace::prevalidate_start(&self.root, exercise) {
                return outcome;
            }
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
            "{}\t{}\tProblem: {}\tQuestion: {}",
            exercise.id,
            exercise.problem.title,
            exercise.problem.id,
            exercise.problem.question_doc.unwrap()
        );
    }
}

fn bindings(problem: &Problem) -> Vec<&'static str> {
    CATALOG
        .iter()
        .filter(|exercise| std::ptr::eq(exercise.problem, problem))
        .map(|exercise| exercise.id)
        .collect()
}

pub fn questions(pretty: bool) {
    if !pretty {
        let inventory: Vec<_> = PROBLEMS.iter().map(|problem| serde_json::json!({
            "id": problem.id,
            "title": problem.title,
            "question_status": problem.question_status.to_string(),
            "question_doc": problem.question_doc,
            "references": problem.references.iter().map(|reference| serde_json::json!({
                "language": reference.language, "path": reference.path, "note": reference.note
            })).collect::<Vec<_>>(),
            "bindings": bindings(problem),
        })).collect();
        println!("{}", serde_json::Value::from(inventory));
        return;
    }
    println!("{}", questions_table());
}

// The catalog's identifiers and language names are ASCII. Four compact columns
// fit an 80-column terminal; full titles, paths and binding IDs remain in JSON
// and `question ID`. Wrap rather than truncate longer cells.
const TABLE_WIDTHS: [usize; 4] = [35, 8, 18, 12];

fn wrap_cell(value: &str, width: usize) -> Vec<String> {
    assert!(width > 0);
    let mut lines = Vec::new();
    let mut line = String::new();
    for word in value.split_whitespace() {
        if !line.is_empty() && line.chars().count() + 1 + word.chars().count() > width {
            lines.push(std::mem::take(&mut line));
        }
        if !line.is_empty() {
            line.push(' ');
        }
        for character in word.chars() {
            if line.chars().count() == width {
                lines.push(std::mem::take(&mut line));
            }
            line.push(character);
        }
    }
    if !line.is_empty() || lines.is_empty() {
        lines.push(line);
    }
    lines
}

fn table_row(cells: [&str; 4]) -> String {
    format!(
        "{:<35}  {:<8}  {:<18}  {:<12}",
        cells[0], cells[1], cells[2], cells[3]
    )
    .trim_end()
    .to_owned()
}

fn questions_table() -> String {
    let separator = "-".repeat(TABLE_WIDTHS.iter().sum::<usize>() + 6);
    let mut lines = vec![
        table_row(["Problem ID", "Question", "Solutions", "Practice"]),
        separator.clone(),
    ];
    for problem in PROBLEMS {
        let mut languages = Vec::new();
        for reference in problem.references {
            if !languages.contains(&reference.language) {
                languages.push(reference.language);
            }
        }
        let mut practice = Vec::new();
        for exercise in CATALOG
            .iter()
            .filter(|exercise| std::ptr::eq(exercise.problem, *problem))
        {
            let language = exercise.language.to_string();
            if !practice.contains(&language) {
                practice.push(language);
            }
        }
        let values = [
            problem.id.to_owned(),
            problem.question_status.to_string(),
            if languages.is_empty() {
                "-".into()
            } else {
                languages.join(", ")
            },
            if practice.is_empty() {
                "-".into()
            } else {
                practice.join(", ")
            },
        ];
        let cells: Vec<_> = values
            .iter()
            .zip(TABLE_WIDTHS)
            .map(|(value, width)| wrap_cell(value, width))
            .collect();
        for row in 0..cells.iter().map(Vec::len).max().unwrap_or(0) {
            lines.push(table_row(std::array::from_fn(|column| {
                cells[column].get(row).map(String::as_str).unwrap_or("")
            })));
        }
    }
    lines.push(separator);
    lines.push(format!(
        "Total: {} topics | {} docs | {} solution artifacts | {} native bindings",
        PROBLEMS.len(),
        PROBLEMS
            .iter()
            .filter(|problem| problem.question_doc.is_some())
            .count(),
        PROBLEMS
            .iter()
            .map(|problem| problem.references.len())
            .sum::<usize>(),
        CATALOG.len()
    ));
    lines.push("Practice: runnable languages; '-' means not converted.".into());
    lines.push("Solutions: implementation languages (not all checked); '-' means none.".into());
    lines.push("Details and exact binding IDs: polyglot question <problem-id>".into());
    lines.join("\n")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pretty_inventory_fits_eighty_columns_without_tabs_or_lost_ids() {
        let table = questions_table();
        assert!(!table.contains('\t'));
        assert!(table.is_ascii());
        assert!(table.lines().all(|line| line.len() < 80));
        let header = table.lines().next().unwrap();
        assert_eq!(header.find("Question"), Some(37));
        assert_eq!(header.find("Solutions"), Some(47));
        assert_eq!(header.find("Practice"), Some(67));
        for problem in PROBLEMS {
            assert_eq!(
                table
                    .lines()
                    .filter(|line| line.starts_with(&format!("{} ", problem.id)))
                    .count(),
                1,
                "{} must remain visible exactly once",
                problem.id
            );
        }
    }

    #[test]
    fn table_cells_wrap_without_truncation() {
        assert_eq!(wrap_cell("abcdefghij", 4), ["abcd", "efgh", "ij"]);
        let references = "python, javascript, go, bash, lua, lisp";
        let lines = wrap_cell(references, 18);
        assert!(lines.iter().all(|line| line.len() <= 18));
        assert!(lines.len() > 1);
        assert_eq!(lines.join(" "), references);
    }
}
