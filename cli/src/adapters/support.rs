use std::fs;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};

use crate::model::Outcome;

pub(super) struct Scratch {
    pub path: PathBuf,
}

impl Scratch {
    pub fn new(label: &str) -> Result<Self, Outcome> {
        static NEXT: AtomicU64 = AtomicU64::new(0);
        if !label
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b == b'-')
        {
            return Err(Outcome::Blocked("invalid scratch label".into()));
        }
        for _ in 0..100 {
            let path = std::env::temp_dir().join(format!(
                "polyglot-{label}-{}-{}",
                std::process::id(),
                NEXT.fetch_add(1, Ordering::Relaxed)
            ));
            let mut builder = fs::DirBuilder::new();
            #[cfg(unix)]
            {
                use std::os::unix::fs::DirBuilderExt;
                builder.mode(0o700);
            }
            match builder.create(&path) {
                Ok(()) => return Ok(Self { path }),
                Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => continue,
                Err(error) => return Err(Outcome::Blocked(format!("scratch directory: {error}"))),
            }
        }
        Err(Outcome::Blocked(
            "could not allocate exclusive scratch directory".into(),
        ))
    }
}

impl Drop for Scratch {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.path);
    }
}
