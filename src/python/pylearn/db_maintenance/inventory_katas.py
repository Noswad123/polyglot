import os
import shutil

LANGUAGES_ROOT = "src/languages"
README_KATAS_DIR = "README/katas"


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def backup_file(path):
    if os.path.exists(path):
        backup_path = path + ".bak"
        print(f"Backing up {path} -> {backup_path}")
        shutil.copy2(path, backup_path)


def find_katas_by_language():
    inventory = {}  # {kata_name: {language: {'has_test': True/False, 'code_files': []}}}
    languages = [d for d in os.listdir(LANGUAGES_ROOT) if os.path.isdir(
        os.path.join(LANGUAGES_ROOT, d))]

    for lang in languages:
        katas_dir = os.path.join(LANGUAGES_ROOT, lang, 'katas')
        if not os.path.isdir(katas_dir):
            continue
        files = [f for f in os.listdir(katas_dir) if os.path.isfile(
            os.path.join(katas_dir, f))]
        for f in files:
            name, ext = os.path.splitext(f)
            # Get just the base problem name (without 'test' if it's a test file)
            kata_name = name.replace('test', '').replace(
                'Test', '').lstrip('_').rstrip('_')
            if not kata_name:
                kata_name = name
            if kata_name not in inventory:
                inventory[kata_name] = {}
            if lang not in inventory[kata_name]:
                inventory[kata_name][lang] = {
                    'has_test': False, 'code_files': []}
            # Mark if it's a test
            is_test = 'test' in f.lower() or f.lower().startswith('test')
            if is_test:
                inventory[kata_name][lang]['has_test'] = True
            inventory[kata_name][lang]['code_files'].append(f)
    return inventory


def write_kata_readmes(inventory):
    ensure_dir(README_KATAS_DIR)
    for kata, langs in inventory.items():
        readme_path = os.path.join(README_KATAS_DIR, f"{kata}.md")
        backup_file(readme_path)
        with open(readme_path, 'w') as f:
            f.write(f"# {kata}\n\n")
            f.write("| Language | Implemented | Test | Code Files |\n")
            f.write("|----------|-------------|------|------------|\n")
            for lang in sorted(langs.keys()):
                has_test = "✅" if langs[lang]['has_test'] else ""
                implemented = "✅"
                files_list = ', '.join(langs[lang]['code_files'])
                f.write(f"| {lang} | {implemented} | {
                        has_test} | {files_list} |\n")
            f.write("\n")
    print(f"\nInventory written to {README_KATAS_DIR}/")


if __name__ == "__main__":
    inventory = find_katas_by_language()
    write_kata_readmes(inventory)
