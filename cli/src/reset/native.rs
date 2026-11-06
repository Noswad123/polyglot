use std::ffi::OsStr;
use std::fs::File;
use std::io::{Read, Seek, SeekFrom, Write};
use std::os::unix::fs::PermissionsExt;
use std::path::{Component, Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};

use rustix::fd::OwnedFd;
use rustix::fs::{self, AtFlags, Mode, OFlags, RenameFlags};
use rustix::io::Errno;

use super::{blocked, Outcome, Snapshot};

const DIRECTORY: OFlags = OFlags::RDONLY
    .union(OFlags::DIRECTORY)
    .union(OFlags::NOFOLLOW)
    .union(OFlags::CLOEXEC);

fn unique_name(label: &str) -> String {
    static SERIAL: AtomicU64 = AtomicU64::new(0);
    format!(
        ".polyglot-{label}-{}-{}",
        std::process::id(),
        SERIAL.fetch_add(1, Ordering::Relaxed)
    )
}

// All mutation authority is an open directory handle, never a checked pathname.
struct Directory {
    fd: OwnedFd,
    path: PathBuf,
}

impl Directory {
    fn open(root: &Path, relative: &Path, create: bool) -> std::io::Result<Self> {
        let mut fd = fs::open("/", DIRECTORY, Mode::empty())?;
        for component in root.components() {
            match component {
                Component::RootDir => {}
                Component::Normal(name) => fd = fs::openat(&fd, name, DIRECTORY, Mode::empty())?,
                _ => return Err(std::io::Error::other("invalid absolute reset root")),
            }
        }
        for component in relative.components() {
            let Component::Normal(name) = component else {
                return Err(std::io::Error::other("invalid reset directory"));
            };
            if create {
                match fs::mkdirat(&fd, name, Mode::from_raw_mode(0o700)) {
                    Ok(()) | Err(Errno::EXIST) => {}
                    Err(error) => return Err(error.into()),
                }
            }
            fd = fs::openat(&fd, name, DIRECTORY, Mode::empty())?;
        }
        Ok(Self {
            fd,
            path: root.join(relative),
        })
    }

    fn visible(&self, root: &Path) -> Result<(), Outcome> {
        let current = Self::open(root, self.path.strip_prefix(root).map_err(blocked)?, false)
            .map_err(blocked)?;
        let before = fs::fstat(&self.fd).map_err(blocked)?;
        let after = fs::fstat(&current.fd).map_err(blocked)?;
        if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino) {
            return Err(blocked("directory changed during reset; install refused"));
        }
        Ok(())
    }

    fn exclusive(&self, label: &str) -> Result<(String, File), Outcome> {
        for _ in 0..100 {
            let name = unique_name(label);
            match fs::openat(
                &self.fd,
                &name,
                OFlags::RDWR | OFlags::CREATE | OFlags::EXCL | OFlags::NOFOLLOW | OFlags::CLOEXEC,
                Mode::from_raw_mode(0o600),
            ) {
                Ok(fd) => return Ok((name, File::from(fd))),
                Err(Errno::EXIST) => continue,
                Err(error) => return Err(blocked(error)),
            }
        }
        Err(blocked("could not allocate an exclusive private file"))
    }

    fn read(&self, name: &OsStr) -> std::io::Result<Snapshot> {
        let fd = fs::openat(
            &self.fd,
            name,
            OFlags::RDONLY | OFlags::NOFOLLOW | OFlags::NONBLOCK | OFlags::CLOEXEC,
            Mode::empty(),
        )?;
        read_snapshot(&mut File::from(fd))
    }

    fn remove(&self, name: &str) -> Result<(), Outcome> {
        fs::unlinkat(&self.fd, name, AtFlags::empty()).map_err(blocked)
    }
}

fn read_snapshot(file: &mut File) -> std::io::Result<Snapshot> {
    let metadata = file.metadata()?;
    if !metadata.is_file() {
        return Err(std::io::Error::other("expected a regular exercise file"));
    }
    file.seek(SeekFrom::Start(0))?;
    let mut bytes = Vec::new();
    file.read_to_end(&mut bytes)?;
    Ok(Snapshot {
        bytes,
        modified: metadata.modified()?,
        permissions: metadata.permissions(),
    })
}

pub(super) fn snapshot(root: &Path, relative: &Path) -> Result<Option<Snapshot>, Outcome> {
    let result = Directory::open(root, relative.parent().unwrap(), false)
        .and_then(|directory| directory.read(relative.file_name().unwrap()));
    match result {
        Ok(snapshot) => Ok(Some(snapshot)),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(None),
        Err(error) => Err(blocked(error)),
    }
}

fn write_backup(file: &mut File, bytes: &[u8]) -> Result<(), Outcome> {
    file.seek(SeekFrom::Start(0)).map_err(blocked)?;
    file.set_len(0).map_err(blocked)?;
    file.write_all(bytes).map_err(blocked)?;
    file.sync_all().map_err(blocked)?;
    file.seek(SeekFrom::Start(0)).map_err(blocked)?;
    let mut verified = Vec::new();
    file.read_to_end(&mut verified).map_err(blocked)?;
    if verified != bytes {
        return Err(blocked("backup verification failed"));
    }
    Ok(())
}

// Keep the actual inode permanently: an editor can still write through a held
// descriptor even after both snapshot reads agree. Never copy-and-unlink it.
fn retain_displaced(
    parent: &Directory,
    temporary: &str,
    backup_directory: &Directory,
    backup: &mut File,
    initial: &Snapshot,
    after_verification: impl FnOnce(),
) -> Result<PathBuf, Outcome> {
    let mut recovery = parent.path.join(temporary);
    let result = (|| {
        let fd = fs::openat(
            &parent.fd,
            temporary,
            OFlags::RDONLY | OFlags::NOFOLLOW | OFlags::NONBLOCK | OFlags::CLOEXEC,
            Mode::empty(),
        )
        .map_err(blocked)?;
        let mut file = File::from(fd);
        let metadata = file.metadata().map_err(blocked)?;
        if !metadata.is_file() {
            return Err(blocked("displaced recovery artifact is not a regular file"));
        }
        fs::fchmod(
            &file,
            Mode::from_raw_mode((metadata.permissions().mode() & 0o600) as _),
        )
        .map_err(blocked)?;
        for _ in 0..100 {
            let name = unique_name("recovery");
            match fs::renameat_with(
                &parent.fd,
                temporary,
                &backup_directory.fd,
                &name,
                RenameFlags::NOREPLACE,
            ) {
                Ok(()) => {
                    recovery = backup_directory.path.join(name);
                    break;
                }
                Err(Errno::EXIST) => continue,
                // Keep the private adjacent inode if a safe move isn't supported.
                Err(Errno::XDEV | Errno::OPNOTSUPP | Errno::NOSYS | Errno::INVAL) => break,
                Err(error) => return Err(blocked(error)),
            }
        }
        file.sync_all().map_err(blocked)?;
        fs::fsync(&backup_directory.fd).map_err(blocked)?;
        fs::fsync(&parent.fd).map_err(blocked)?;
        let actual = read_snapshot(&mut file).map_err(blocked)?;
        write_backup(backup, &actual.bytes)?;
        fs::fsync(&backup_directory.fd).map_err(blocked)?;
        let verified = read_snapshot(&mut file).map_err(blocked)?;
        after_verification();
        if actual.bytes != verified.bytes || actual.modified != verified.modified {
            return Err(blocked("displaced file changed while backing it up"));
        }
        if actual.bytes != initial.bytes {
            return Err(blocked("late exercise edit detected; actual displaced bytes were backed up; no rollback was attempted"));
        }
        Ok(())
    })();
    println!("Recovery: {}", recovery.display());
    result.map(|()| recovery.clone()).map_err(|error| {
        blocked(format!(
            "baseline was installed, but {error}. Recovery: {}",
            recovery.display()
        ))
    })
}

pub(super) fn install(
    root: &Path,
    relative: &Path,
    baseline: &[u8],
    initial: &Option<Snapshot>,
    before_install: impl FnOnce() -> Result<(), Outcome>,
) -> Result<(), Outcome> {
    let parent = Directory::open(root, relative.parent().unwrap(), true).map_err(blocked)?;
    let mut backup = if let Some(source) = initial {
        let directory =
            Directory::open(root, Path::new(".polyglot/backups"), true).map_err(blocked)?;
        let (name, mut file) = directory.exclusive("backup")?;
        if let Err(error) = write_backup(&mut file, &source.bytes) {
            let _ = directory.remove(&name);
            return Err(error);
        }
        println!("Backup: {}", directory.path.join(&name).display());
        Some((directory, file))
    } else {
        None
    };
    let (temporary, mut file) = parent.exclusive("reset")?;
    let prepared = (|| {
        file.write_all(baseline).map_err(blocked)?;
        if let Some(source) = initial {
            file.set_permissions(source.permissions.clone())
                .map_err(blocked)?;
        }
        file.sync_all().map_err(blocked)?;
        before_install()?;
        parent.visible(root)?;
        if let Some((directory, _)) = &backup {
            directory.visible(root)?;
        }
        let flags = if initial.is_some() {
            RenameFlags::EXCHANGE
        } else {
            RenameFlags::NOREPLACE
        };
        fs::renameat_with(
            &parent.fd,
            &temporary,
            &parent.fd,
            relative.file_name().unwrap(),
            flags,
        )
        .map_err(|error| {
            blocked(format!(
                "conditional atomic install refused ({error}); no overwrite fallback is used"
            ))
        })
    })();
    if prepared.is_err() {
        let _ = parent.remove(&temporary);
    }
    prepared?;
    if let (Some(source), Some((directory, file))) = (initial, &mut backup) {
        retain_displaced(&parent, &temporary, directory, file, source, || {})?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs as stdfs;
    use std::os::unix::fs::symlink;

    struct Fixture(PathBuf);

    impl Fixture {
        fn new() -> Self {
            static SERIAL: AtomicU64 = AtomicU64::new(0);
            let root = std::env::temp_dir().join(format!(
                "polyglot-native-reset-{}-{}",
                std::process::id(),
                SERIAL.fetch_add(1, Ordering::Relaxed)
            ));
            stdfs::create_dir(&root).unwrap();
            // Canonical paths avoid macOS's /var -> /private/var alias.
            let root = root.canonicalize().unwrap();
            stdfs::create_dir(root.join("exercises")).unwrap();
            Self(root)
        }

        fn source(&self) -> PathBuf {
            self.0.join("exercises/hello.py")
        }

        fn backups(&self) -> Vec<PathBuf> {
            stdfs::read_dir(self.0.join(".polyglot/backups"))
                .unwrap()
                .map(|entry| entry.unwrap().path())
                .filter(|path| {
                    path.file_name()
                        .unwrap()
                        .to_string_lossy()
                        .starts_with(".polyglot-backup-")
                })
                .collect()
        }

        fn recovery(&self) -> PathBuf {
            stdfs::read_dir(self.0.join(".polyglot/backups"))
                .unwrap()
                .map(|entry| entry.unwrap().path())
                .find(|path| {
                    path.file_name()
                        .unwrap()
                        .to_string_lossy()
                        .starts_with(".polyglot-recovery-")
                })
                .unwrap()
        }
    }

    impl Drop for Fixture {
        fn drop(&mut self) {
            stdfs::remove_dir_all(&self.0).unwrap();
        }
    }

    #[test]
    fn missing_file_appearing_at_install_is_not_overwritten() {
        let fixture = Fixture::new();
        let result = install(
            &fixture.0,
            Path::new("exercises/hello.py"),
            b"baseline",
            &None,
            || {
                stdfs::write(fixture.source(), b"late new file").unwrap();
                Ok(())
            },
        );
        assert!(result.is_err());
        assert_eq!(stdfs::read(fixture.source()).unwrap(), b"late new file");
        assert!(!fixture.0.join(".polyglot").exists());
        assert_eq!(
            stdfs::read_dir(fixture.0.join("exercises"))
                .unwrap()
                .count(),
            1
        );
    }

    #[test]
    fn exchange_retains_actual_late_edit_and_reports_blocked_recovery() {
        let fixture = Fixture::new();
        stdfs::write(fixture.source(), b"initial").unwrap();
        let initial = snapshot(&fixture.0, Path::new("exercises/hello.py")).unwrap();
        let result = install(
            &fixture.0,
            Path::new("exercises/hello.py"),
            b"baseline",
            &initial,
            || {
                // An editor's atomic save after final validation, before EXCHANGE.
                let save = fixture.0.join("editor-save");
                stdfs::write(&save, b"latest learner edit\x00\xff\n").unwrap();
                stdfs::rename(save, fixture.source()).unwrap();
                Ok(())
            },
        );
        let error = result.unwrap_err().to_string();
        assert!(error.contains("baseline was installed"), "{error}");
        assert!(error.contains("Recovery:"), "{error}");
        assert_eq!(stdfs::read(fixture.source()).unwrap(), b"baseline");
        assert_eq!(
            stdfs::read(&fixture.backups()[0]).unwrap(),
            b"latest learner edit\x00\xff\n"
        );
        assert_eq!(
            stdfs::read(fixture.recovery()).unwrap(),
            b"latest learner edit\x00\xff\n"
        );
    }

    #[test]
    fn backup_failure_after_exchange_keeps_actual_displaced_file() {
        let fixture = Fixture::new();
        stdfs::write(fixture.source(), b"initial").unwrap();
        let initial = snapshot(&fixture.0, Path::new("exercises/hello.py"))
            .unwrap()
            .unwrap();
        let parent = Directory::open(&fixture.0, Path::new("exercises"), false).unwrap();
        let backups = Directory::open(&fixture.0, Path::new(".polyglot/backups"), true).unwrap();
        let (backup_name, mut backup) = backups.exclusive("backup").unwrap();
        write_backup(&mut backup, b"initial").unwrap();
        let (temporary, mut file) = parent.exclusive("reset").unwrap();
        file.write_all(b"baseline").unwrap();
        stdfs::write(fixture.source(), b"latest learner bytes").unwrap();
        fs::renameat_with(
            &parent.fd,
            &temporary,
            &parent.fd,
            "hello.py",
            RenameFlags::EXCHANGE,
        )
        .unwrap();
        // A read-only descriptor deterministically simulates a failed backup write.
        let mut failed_backup = File::open(backups.path.join(backup_name)).unwrap();
        let error = retain_displaced(
            &parent,
            &temporary,
            &backups,
            &mut failed_backup,
            &initial,
            || {},
        )
        .unwrap_err()
        .to_string();
        assert!(error.contains("Recovery:"), "{error}");
        assert_eq!(
            stdfs::read(fixture.recovery()).unwrap(),
            b"latest learner bytes"
        );
        assert_eq!(stdfs::read(fixture.source()).unwrap(), b"baseline");
    }

    #[test]
    fn held_editor_descriptor_can_write_recovery_after_snapshot_verification() {
        let fixture = Fixture::new();
        stdfs::write(fixture.source(), b"initial").unwrap();
        let initial = snapshot(&fixture.0, Path::new("exercises/hello.py"))
            .unwrap()
            .unwrap();
        let mut editor = stdfs::OpenOptions::new()
            .write(true)
            .open(fixture.source())
            .unwrap();
        let parent = Directory::open(&fixture.0, Path::new("exercises"), false).unwrap();
        let backups = Directory::open(&fixture.0, Path::new(".polyglot/backups"), true).unwrap();
        let (_, mut backup) = backups.exclusive("backup").unwrap();
        let (temporary, mut baseline) = parent.exclusive("reset").unwrap();
        baseline.write_all(b"baseline").unwrap();
        fs::renameat_with(
            &parent.fd,
            &temporary,
            &parent.fd,
            "hello.py",
            RenameFlags::EXCHANGE,
        )
        .unwrap();
        let recovery =
            retain_displaced(&parent, &temporary, &backups, &mut backup, &initial, || {
                editor.set_len(0).unwrap();
                editor.write_all(b"late held-descriptor save").unwrap();
                editor.sync_all().unwrap();
            })
            .unwrap();
        assert_eq!(
            stdfs::read(&recovery).unwrap(),
            b"late held-descriptor save"
        );
        assert_eq!(
            stdfs::metadata(&recovery).unwrap().permissions().mode() & 0o777,
            0o600
        );
        assert_eq!(stdfs::read(&fixture.backups()[0]).unwrap(), b"initial");
        assert_eq!(stdfs::read(fixture.source()).unwrap(), b"baseline");
        // The recovery inode also remains reachable for writes after completion.
        editor.write_all(b" after completion").unwrap();
        assert_eq!(
            stdfs::read(recovery).unwrap(),
            b"late held-descriptor save after completion"
        );
    }

    #[test]
    fn backup_directory_swap_cannot_redirect_exclusive_create() {
        let fixture = Fixture::new();
        let directory = Directory::open(&fixture.0, Path::new(".polyglot/backups"), true).unwrap();
        let retained = fixture.0.join("retained-backups");
        let outside = fixture.0.join("outside");
        stdfs::create_dir(&outside).unwrap();
        stdfs::rename(&directory.path, &retained).unwrap();
        symlink(&outside, &directory.path).unwrap();
        let (name, mut file) = directory.exclusive("backup").unwrap();
        assert_eq!(file.metadata().unwrap().permissions().mode() & 0o777, 0o600);
        file.write_all(b"private bytes").unwrap();
        assert_eq!(stdfs::read(retained.join(name)).unwrap(), b"private bytes");
        assert_eq!(stdfs::read_dir(outside).unwrap().count(), 0);
        assert!(directory.visible(&fixture.0).is_err());
    }

    #[test]
    fn backup_directory_redirect_before_install_blocks_without_source_change() {
        let fixture = Fixture::new();
        stdfs::write(fixture.source(), b"initial").unwrap();
        let initial = snapshot(&fixture.0, Path::new("exercises/hello.py")).unwrap();
        let outside = fixture.0.join("outside");
        stdfs::create_dir(&outside).unwrap();
        let result = install(
            &fixture.0,
            Path::new("exercises/hello.py"),
            b"baseline",
            &initial,
            || {
                let backups = fixture.0.join(".polyglot/backups");
                stdfs::rename(&backups, fixture.0.join("retained-backups")).unwrap();
                symlink(&outside, backups).unwrap();
                Ok(())
            },
        );
        assert!(result.is_err());
        assert_eq!(stdfs::read(fixture.source()).unwrap(), b"initial");
        assert_eq!(stdfs::read_dir(outside).unwrap().count(), 0);
    }

    #[test]
    fn source_parent_redirect_before_install_is_not_followed() {
        let fixture = Fixture::new();
        stdfs::write(fixture.source(), b"initial").unwrap();
        let initial = snapshot(&fixture.0, Path::new("exercises/hello.py")).unwrap();
        let outside = fixture.0.join("outside");
        stdfs::create_dir(&outside).unwrap();
        stdfs::write(outside.join("hello.py"), b"outside untouched").unwrap();
        let result = install(
            &fixture.0,
            Path::new("exercises/hello.py"),
            b"baseline",
            &initial,
            || {
                let parent = fixture.0.join("exercises");
                stdfs::rename(&parent, fixture.0.join("retained-exercises")).unwrap();
                symlink(&outside, parent).unwrap();
                Ok(())
            },
        );
        assert!(result.is_err());
        assert_eq!(
            stdfs::read(fixture.0.join("retained-exercises/hello.py")).unwrap(),
            b"initial"
        );
        assert_eq!(
            stdfs::read(outside.join("hello.py")).unwrap(),
            b"outside untouched"
        );
    }

    #[test]
    fn backup_files_and_new_directories_are_private_from_creation() {
        let fixture = Fixture::new();
        stdfs::write(fixture.source(), b"private learner bytes").unwrap();
        stdfs::set_permissions(fixture.source(), stdfs::Permissions::from_mode(0o600)).unwrap();
        let initial = snapshot(&fixture.0, Path::new("exercises/hello.py")).unwrap();
        install(
            &fixture.0,
            Path::new("exercises/hello.py"),
            b"baseline",
            &initial,
            || {
                assert_eq!(
                    stdfs::metadata(&fixture.backups()[0])
                        .unwrap()
                        .permissions()
                        .mode()
                        & 0o777,
                    0o600
                );
                for name in [".polyglot", ".polyglot/backups"] {
                    assert_eq!(
                        stdfs::metadata(fixture.0.join(name))
                            .unwrap()
                            .permissions()
                            .mode()
                            & 0o777,
                        0o700
                    );
                }
                Ok(())
            },
        )
        .unwrap();
        assert_eq!(
            stdfs::metadata(fixture.source())
                .unwrap()
                .permissions()
                .mode()
                & 0o777,
            0o600
        );
        assert_eq!(
            stdfs::read(&fixture.backups()[0]).unwrap(),
            b"private learner bytes"
        );
        assert_eq!(
            stdfs::read_dir(fixture.0.join("exercises"))
                .unwrap()
                .count(),
            1
        );
    }
}
