from pathlib import Path
from ...config import LANGUAGES_ROOT, PROJECT_ROOT

if PROJECT_ROOT is not None:
    README_KATAS_DIR = PROJECT_ROOT / "README" / "katas"

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def backup_file(path: Path):
    if path.exists():
        backup_path = path.with_suffix(path.suffix + ".bak")
        print(f"Backing up {path} -> {backup_path}")
        import shutil
        shutil.copy2(path, backup_path)

def find_katas_by_language():
    inventory = {}

    for lang_dir in LANGUAGES_ROOT.iterdir():
        if not lang_dir.is_dir():
            continue

        lang = lang_dir.name
        katas_dir = lang_dir / "katas"
        if not katas_dir.is_dir():
            continue

        for file in katas_dir.iterdir():
            if not file.is_file():
                continue

            name = file.stem
            kata_name = (
                name.replace("test", "").replace("Test", "")
                    .lstrip("_").rstrip("_") or name
            )

            entry = inventory.setdefault(kata_name, {})
            lang_entry = entry.setdefault(lang, {
                "has_test": False,
                "code_files": []
            })

            if "test" in file.name.lower() or file.name.lower().startswith("test"):
                lang_entry["has_test"] = True

            lang_entry["code_files"].append(file.name)

    return inventory

def write_kata_readmes(inventory):
    ensure_dir(README_KATAS_DIR)

    for kata, langs in inventory.items():
        readme_path = README_KATAS_DIR / f"{kata}.md"
        backup_file(readme_path)

        with readme_path.open("w") as f:
            f.write(f"# {kata}\n\n")
            f.write("| Language | Implemented | Test | Code Files |\n")
            f.write("|----------|-------------|------|------------|\n")
            for lang in sorted(langs.keys()):
                has_test = "✅" if langs[lang]["has_test"] else ""
                implemented = "✅"
                files_list = ", ".join(langs[lang]["code_files"])
                f.write(f"| {lang} | {implemented} | {has_test} | {files_list} |\n")
            f.write("\n")

    print(f"\nInventory written to {README_KATAS_DIR}/")

def inventory_katas():
    inv = find_katas_by_language()
    write_kata_readmes(inv)
