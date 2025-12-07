import os
from .config import LANGUAGES_ROOT, PROJECT_ROOT

README_KATAS_DIR = PROJECT_ROOT / "README" / "katas"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def backup_file(path):
    if os.path.exists(path):
        backup_path = path + ".bak"
        print(f"Backing up {path} -> {backup_path}")
        import shutil
        shutil.copy2(path, backup_path)

def find_katas_by_language():
    inventory = {}
    languages = [
        d for d in os.listdir(LANGUAGES_ROOT)
        if (LANGUAGES_ROOT / d).is_dir()
    ]

    for lang in languages:
        katas_dir = LANGUAGES_ROOT / lang / "katas"
        if not katas_dir.is_dir():
            continue
        files = [
            f for f in os.listdir(katas_dir)
            if (katas_dir / f).is_file()
        ]
        for f in files:
            name, ext = os.path.splitext(f)
            kata_name = name.replace("test", "").replace("Test", "").lstrip("_").rstrip("_") or name
            inventory.setdefault(kata_name, {})
            inventory[kata_name].setdefault(lang, {"has_test": False, "code_files": []})

            is_test = "test" in f.lower() or f.lower().startswith("test")
            if is_test:
                inventory[kata_name][lang]["has_test"] = True
            inventory[kata_name][lang]["code_files"].append(f)
    return inventory

def write_kata_readmes(inventory):
    ensure_dir(README_KATAS_DIR)
    for kata, langs in inventory.items():
        readme_path = README_KATAS_DIR / f"{kata}.md"
        backup_file(str(readme_path))
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
